"""
Landing KPI API Routes - MS SQL Server Version
Updated API endpoints to use MS SQL Server instead of SQLite for KPI storage.
"""

import logging
from flask import Blueprint, request, jsonify
from typing import Dict, Any
import time

from kg_builder.services.landing_kpi_service_mssql import LandingKPIServiceMSSQL
from kg_builder.services.enhanced_sql_generator import EnhancedSQLGenerator
from kg_builder.services.nl_query_executor import NLQueryExecutor
from kg_builder.services.llm_sql_generator import LLMSQLGenerator

logger = logging.getLogger(__name__)

# Create Blueprint
landing_kpi_mssql_bp = Blueprint('landing_kpi_mssql', __name__, url_prefix='/v1/landing-kpi-mssql')

# Initialize services
kpi_service = LandingKPIServiceMSSQL()


@landing_kpi_mssql_bp.route('/kpis', methods=['GET'])
def get_all_kpis():
    """Get all KPIs with their latest execution status."""
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        kpis = kpi_service.get_all_kpis(include_inactive=include_inactive)
        
        return jsonify({
            'success': True,
            'data': kpis,
            'count': len(kpis),
            'storage_type': 'mssql'
        })
    except Exception as e:
        logger.error(f"Error getting KPIs: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@landing_kpi_mssql_bp.route('/kpis', methods=['POST'])
def create_kpi():
    """Create a new KPI definition."""
    try:
        kpi_data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'nl_definition']
        for field in required_fields:
            if not kpi_data.get(field):
                return jsonify({
                    'success': False, 
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Add user info if available
        kpi_data['created_by'] = request.headers.get('X-User-ID', 'api_user')
        
        kpi = kpi_service.create_kpi(kpi_data)
        
        return jsonify({
            'success': True,
            'data': kpi,
            'message': f'KPI "{kpi["name"]}" created successfully'
        }), 201
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating KPI: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@landing_kpi_mssql_bp.route('/kpis/<int:kpi_id>', methods=['GET'])
def get_kpi(kpi_id):
    """Get KPI by ID."""
    try:
        kpi = kpi_service.get_kpi(kpi_id)
        if not kpi:
            return jsonify({'success': False, 'error': 'KPI not found'}), 404
        
        return jsonify({'success': True, 'data': kpi})
    except Exception as e:
        logger.error(f"Error getting KPI {kpi_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@landing_kpi_mssql_bp.route('/kpis/<int:kpi_id>', methods=['PUT'])
def update_kpi(kpi_id):
    """Update KPI definition."""
    try:
        kpi_data = request.get_json()
        kpi = kpi_service.update_kpi(kpi_id, kpi_data)
        
        return jsonify({
            'success': True,
            'data': kpi,
            'message': f'KPI updated successfully'
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error updating KPI {kpi_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@landing_kpi_mssql_bp.route('/kpis/<int:kpi_id>', methods=['DELETE'])
def delete_kpi(kpi_id):
    """Delete (deactivate) KPI."""
    try:
        success = kpi_service.delete_kpi(kpi_id)
        if not success:
            return jsonify({'success': False, 'error': 'KPI not found'}), 404
        
        return jsonify({
            'success': True,
            'message': 'KPI deactivated successfully'
        })
    except Exception as e:
        logger.error(f"Error deleting KPI {kpi_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@landing_kpi_mssql_bp.route('/kpis/<int:kpi_id>/execute', methods=['POST'])
def execute_kpi(kpi_id):
    """Execute a KPI and store results in MS SQL Server."""
    try:
        # Get KPI definition
        kpi = kpi_service.get_kpi(kpi_id)
        if not kpi:
            return jsonify({'success': False, 'error': 'KPI not found'}), 404
        
        # Get execution parameters
        execution_params = request.get_json() or {}
        execution_params.update({
            'user_id': request.headers.get('X-User-ID', 'api_user'),
            'session_id': request.headers.get('X-Session-ID')
        })
        
        # Create execution record
        execution_record = kpi_service.create_execution_record(kpi_id, execution_params)
        execution_id = execution_record['id']
        
        start_time = time.time()
        
        try:
            # Initialize enhanced SQL generator
            original_generator = LLMSQLGenerator()
            enhanced_generator = EnhancedSQLGenerator(original_generator)
            
            # Initialize query executor with enhanced generator
            executor = NLQueryExecutor()
            executor.sql_generator = enhanced_generator  # Use enhanced generator
            
            # Execute the KPI query
            result = executor.execute_query(
                query=kpi['nl_definition'],
                kg_name=execution_params.get('kg_name', 'default'),
                select_schema=execution_params.get('select_schema', 'newdqschemanov'),
                limit_records=execution_params.get('limit_records', 1000)
            )
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Prepare result data for storage (with both original and enhanced SQL)
            generated_sql = result.get('generated_sql')

            # Check if SQL was enhanced with material master and ops_planner
            from kg_builder.services.material_master_enhancer import material_master_enhancer
            enhancement_result = material_master_enhancer.enhance_sql_with_material_master(generated_sql) if generated_sql else None

            result_data = {
                'generated_sql': generated_sql,  # Original SQL
                'enhanced_sql': enhancement_result['enhanced_sql'] if enhancement_result and enhancement_result['enhancement_applied'] else generated_sql,  # Enhanced SQL
                'number_of_records': len(result.get('data', [])),
                'joined_columns': result.get('joined_columns', []),
                'sql_query_type': result.get('query_type'),
                'operation': result.get('operation'),
                'execution_status': 'success' if result.get('success') else 'error',
                'execution_time_ms': execution_time_ms,
                'confidence_score': result.get('confidence_score'),
                'error_message': result.get('error'),
                'result_data': result.get('data', []),
                'evidence_data': result.get('evidence_data', []),
                'source_table': result.get('source_table'),
                'target_table': result.get('target_table')
            }
            
            # Update execution record with results
            updated_execution = kpi_service.update_execution_result(execution_id, result_data)
            
            return jsonify({
                'success': True,
                'data': {
                    'execution_id': execution_id,
                    'kpi_name': kpi['name'],
                    'kpi_alias_name': kpi['alias_name'],
                    'execution_status': result_data['execution_status'],
                    'generated_sql': result_data['generated_sql'],  # Always include SQL
                    'number_of_records': result_data['number_of_records'],
                    'execution_time_ms': execution_time_ms,
                    'evidence_count': len(result_data['evidence_data']),
                    'error_message': result_data.get('error_message')
                },
                'storage_type': 'mssql'
            })
            
        except Exception as exec_error:
            # Store execution error but still include generated SQL if available
            execution_time_ms = (time.time() - start_time) * 1000
            
            error_result_data = {
                'generated_sql': getattr(exec_error, 'generated_sql', None),  # Try to get SQL even on error
                'execution_status': 'error',
                'execution_time_ms': execution_time_ms,
                'error_message': str(exec_error),
                'number_of_records': 0
            }
            
            kpi_service.update_execution_result(execution_id, error_result_data)
            
            return jsonify({
                'success': False,
                'error': str(exec_error),
                'execution_id': execution_id,
                'generated_sql': error_result_data.get('generated_sql'),  # Include SQL even on error
                'storage_type': 'mssql'
            }), 500
            
    except Exception as e:
        logger.error(f"Error executing KPI {kpi_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@landing_kpi_mssql_bp.route('/kpis/<int:kpi_id>/executions', methods=['GET'])
def get_kpi_executions(kpi_id):
    """Get execution history for a KPI."""
    try:
        limit = int(request.args.get('limit', 10))
        executions = kpi_service.get_kpi_executions(kpi_id, limit=limit)

        return jsonify({
            'success': True,
            'data': executions,
            'count': len(executions),
            'kpi_id': kpi_id,
            'storage_type': 'mssql'
        })
    except Exception as e:
        logger.error(f"Error getting executions for KPI {kpi_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@landing_kpi_mssql_bp.route('/executions/<int:execution_id>', methods=['GET'])
def get_execution_result(execution_id):
    """Get detailed execution result by ID."""
    try:
        execution = kpi_service.get_execution_result(execution_id)
        if not execution:
            return jsonify({'success': False, 'error': 'Execution not found'}), 404

        return jsonify({
            'success': True,
            'data': execution,
            'storage_type': 'mssql'
        })
    except Exception as e:
        logger.error(f"Error getting execution {execution_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@landing_kpi_mssql_bp.route('/sql-preview', methods=['POST'])
def preview_sql():
    """Preview generated SQL for a query without executing it."""
    try:
        request_data = request.get_json()
        query = request_data.get('query')

        if not query:
            return jsonify({'success': False, 'error': 'Query is required'}), 400

        # Initialize enhanced SQL generator
        original_generator = LLMSQLGenerator()
        enhanced_generator = EnhancedSQLGenerator(original_generator)

        # Initialize query executor with enhanced generator
        executor = NLQueryExecutor()
        executor.sql_generator = enhanced_generator

        # Generate SQL without executing
        try:
            # Parse the query to get intent
            query_intent = executor.query_parser.parse_query(query)

            # Get KG data
            kg_data = executor.kg_service.get_kg_data(
                request_data.get('kg_name', 'default'),
                request_data.get('select_schema', 'newdqschemanov')
            )

            # Generate enhanced SQL
            generated_sql = enhanced_generator.generate_sql(query_intent, kg_data)

            return jsonify({
                'success': True,
                'data': {
                    'query': query,
                    'generated_sql': generated_sql,  # Always show generated SQL
                    'query_intent': query_intent,
                    'includes_ops_planner': 'ops_planner' in (generated_sql or '').lower(),
                    'involves_hana_master': 'hana_material_master' in (generated_sql or '').lower()
                },
                'storage_type': 'mssql'
            })

        except Exception as gen_error:
            # Even if generation fails, try to show partial results
            return jsonify({
                'success': False,
                'error': str(gen_error),
                'data': {
                    'query': query,
                    'generated_sql': getattr(gen_error, 'generated_sql', None),
                    'partial_result': True
                },
                'storage_type': 'mssql'
            }), 500

    except Exception as e:
        logger.error(f"Error in SQL preview: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@landing_kpi_mssql_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get dashboard data with KPIs grouped by group name and their latest execution status."""
    try:
        dashboard_data = kpi_service.get_dashboard_data()

        return jsonify({
            'success': True,
            **dashboard_data,
            'storage_type': 'mssql'
        })
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@landing_kpi_mssql_bp.route('/<int:kpi_id>/latest-results', methods=['GET'])
def get_latest_results(kpi_id):
    """Get the latest execution results for a specific KPI."""
    try:
        results = kpi_service.get_latest_results(kpi_id)

        if not results:
            return jsonify({
                'success': False,
                'error': f'No execution results found for KPI {kpi_id}'
            }), 404

        return jsonify({
            'success': True,
            'results': results,
            'storage_type': 'mssql'
        })
    except Exception as e:
        logger.error(f"Error getting latest results for KPI {kpi_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@landing_kpi_mssql_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for KPI Analytics service."""
    try:
        # Test database connection
        kpis = kpi_service.get_all_kpis(limit=1)

        return jsonify({
            'success': True,
            'status': 'healthy',
            'database': 'mssql',
            'service': 'kpi_analytics',
            'timestamp': time.time()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 500
