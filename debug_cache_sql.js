// Debug script to test KPI cache SQL storage
// Run this in browser console on KPI Management page

async function debugCacheSQLStorage(kpiId) {
    console.log(`🔍 Debugging cache SQL storage for KPI ${kpiId}`);
    console.log('=' * 50);
    
    try {
        // Step 1: Get KPI details
        console.log('1. Getting KPI details...');
        const kpiResponse = await fetch(`/v1/landing-kpi-mssql/kpis`);
        const kpiData = await kpiResponse.json();
        const kpi = kpiData.data.kpis.find(k => k.id === kpiId);
        
        if (!kpi) {
            console.error(`❌ KPI ${kpiId} not found`);
            return;
        }
        
        console.log('✅ KPI found:', kpi.name);
        console.log('   Current isAccept:', kpi.isAccept);
        console.log('   Current isSQLCached:', kpi.isSQLCached);
        console.log('   Current cached_sql exists:', !!kpi.cached_sql);
        
        // Step 2: Get execution history
        console.log('\n2. Getting execution history...');
        const execResponse = await fetch(`/v1/landing-kpi-mssql/kpis/${kpiId}/executions`);
        const execData = await execResponse.json();
        
        console.log('✅ Executions response:', execData);
        const executions = execData.data?.executions || execData.executions || [];
        console.log(`   Found ${executions.length} executions`);
        
        if (executions.length > 0) {
            const latest = executions[0];
            console.log('   Latest execution:');
            console.log('     ID:', latest.id);
            console.log('     Status:', latest.execution_status);
            console.log('     SQL exists:', !!latest.generated_sql);
            if (latest.generated_sql) {
                console.log('     SQL preview:', latest.generated_sql.substring(0, 100) + '...');
            }
        }
        
        // Step 3: Test cache flag update
        console.log('\n3. Testing cache flag update...');
        const updateData = {
            isAccept: true,
            cached_sql: executions.length > 0 ? executions[0].generated_sql : 'SELECT 1 as test'
        };
        
        console.log('   Update data:', updateData);
        
        const updateResponse = await fetch(`/v1/landing-kpi-mssql/kpis/${kpiId}/cache-flags`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updateData)
        });
        
        const updateResult = await updateResponse.json();
        console.log('✅ Update response:', updateResult);
        
        // Step 4: Verify the update
        console.log('\n4. Verifying update...');
        const verifyResponse = await fetch(`/v1/landing-kpi-mssql/kpis`);
        const verifyData = await verifyResponse.json();
        const updatedKpi = verifyData.data.kpis.find(k => k.id === kpiId);
        
        console.log('✅ Updated KPI:');
        console.log('   isAccept:', updatedKpi.isAccept);
        console.log('   isSQLCached:', updatedKpi.isSQLCached);
        console.log('   cached_sql exists:', !!updatedKpi.cached_sql);
        if (updatedKpi.cached_sql) {
            console.log('   cached_sql preview:', updatedKpi.cached_sql.substring(0, 100) + '...');
        }
        
        console.log('\n🎉 Debug completed!');
        
    } catch (error) {
        console.error('❌ Debug failed:', error);
    }
}

// Usage: debugCacheSQLStorage(28)
console.log('Debug function loaded. Run: debugCacheSQLStorage(28)');
