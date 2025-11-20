-- Create Groups table
CREATE TABLE IF NOT EXISTS groups (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(255) NOT NULL UNIQUE,
    description NVARCHAR(1000),
    color NVARCHAR(50),
    icon NVARCHAR(100),
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    created_by NVARCHAR(255),
    updated_by NVARCHAR(255)
);

-- Create Dashboards table
CREATE TABLE IF NOT EXISTS dashboards (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(255) NOT NULL,
    description NVARCHAR(1000),
    group_id INT NOT NULL,
    layout NVARCHAR(MAX),
    widgets NVARCHAR(MAX),
    is_active BIT DEFAULT 1,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    created_by NVARCHAR(255),
    updated_by NVARCHAR(255),
    FOREIGN KEY (group_id) REFERENCES groups(id) ON DELETE CASCADE,
    UNIQUE (group_id, name)
);

-- Create indexes for better query performance
CREATE INDEX idx_groups_is_active ON groups(is_active);
CREATE INDEX idx_dashboards_group_id ON dashboards(group_id);
CREATE INDEX idx_dashboards_is_active ON dashboards(is_active);
CREATE INDEX idx_dashboards_group_active ON dashboards(group_id, is_active);

