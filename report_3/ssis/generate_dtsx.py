#!/usr/bin/env python3
"""
Generate 3 SSIS DTSX packages for the DFF Data Warehouse ETL.

IMPORTANT: After generating, open each .dtsx in Visual Studio (SSDT)
and update the connection strings to match your actual server.

Packages:
  01_Extract_to_Staging.dtsx  — 9 Data Flow Tasks (CSV → staging)
  02_Transform_Staging.dtsx   — Execute SQL Tasks (staging transforms)
  03_Load_DataMart.dtsx       — Execute SQL Tasks (load dims + fact + cleanup)
"""

import uuid
import os
import html

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "sql")

# ---- Configuration ----
SERVER = "infodata16.mbs.tamu.edu"
STAGING_DB = "team1_staging_area"
DW_DB = "team1_dw_area"
CSV_BASE_PATH = r"C:\DFF_Data"  # Update to actual path on server

def new_guid():
    return "{" + str(uuid.uuid4()).upper() + "}"

def escape_xml(s):
    return html.escape(s, quote=True)

# ---- Connection string helpers ----
def oledb_conn(db):
    return (f"Data Source={SERVER};Initial Catalog={db};"
            f"Provider=SQLNCLI11.1;Integrated Security=SSPI;Auto Translate=False;")

def flat_file_conn(filename):
    return os.path.join(CSV_BASE_PATH, filename)

# ---- CSV source definitions ----
CSV_SOURCES = [
    # (task_name, csv_file, staging_table, columns_def)
    ("DFT_Movement_SDR", "wsdr.csv", "stg_Movement_SDR", [
        ("UPC", "DT_I8"), ("STORE", "DT_I4"), ("WEEK", "DT_I4"),
        ("MOVE", "DT_I4"), ("QTY", "DT_I4"), ("PRICE", "DT_R8"),
        ("SALE", "DT_STR", 5), ("PROFIT", "DT_R8"), ("OK", "DT_I4"),
    ]),
    ("DFT_Movement_CSO", "WCSO-Done.csv", "stg_Movement_CSO", [
        ("UPC", "DT_I8"), ("STORE", "DT_I4"), ("WEEK", "DT_I4"),
        ("MOVE", "DT_I4"), ("QTY", "DT_I4"), ("PRICE", "DT_R8"),
        ("SALE", "DT_STR", 5), ("PROFIT", "DT_R8"), ("OK", "DT_I4"),
    ]),
    ("DFT_Movement_TPA", "WTPA_done.csv", "stg_Movement_TPA", [
        ("UPC", "DT_I8"), ("STORE", "DT_I4"), ("WEEK", "DT_I4"),
        ("MOVE", "DT_I4"), ("QTY", "DT_I4"), ("PRICE", "DT_R8"),
        ("SALE", "DT_STR", 5), ("PROFIT", "DT_R8"), ("OK", "DT_I4"),
    ]),
    ("DFT_Movement_CRA", "Done-WCRA.csv", "stg_Movement_CRA", [
        ("UPC", "DT_I8"), ("STORE", "DT_I4"), ("WEEK", "DT_I4"),
        ("MOVE", "DT_I4"), ("QTY", "DT_I4"), ("PRICE", "DT_R8"),
        ("SALE", "DT_STR", 5), ("PROFIT", "DT_R8"), ("OK", "DT_I4"),
    ]),
    ("DFT_Product_SDR", "UPCSDR.csv", "stg_Product_SDR", [
        ("COM_CODE", "DT_I4"), ("UPC", "DT_I8"), ("DESCRIP", "DT_STR", 100),
        ("SIZE", "DT_STR", 30), ("CASE_PACK", "DT_I4"), ("NITEM", "DT_I8"),
    ]),
    ("DFT_Product_CSO", "UPCCSO.csv", "stg_Product_CSO", [
        ("COM_CODE", "DT_I4"), ("UPC", "DT_I8"), ("DESCRIP", "DT_STR", 100),
        ("SIZE", "DT_STR", 30), ("CASE_PACK", "DT_I4"), ("NITEM", "DT_I8"),
    ]),
    ("DFT_Product_TPA", "UPCTPA.csv", "stg_Product_TPA", [
        ("COM_CODE", "DT_I4"), ("UPC", "DT_I8"), ("DESCRIP", "DT_STR", 100),
        ("SIZE", "DT_STR", 30), ("CASE_PACK", "DT_I4"), ("NITEM", "DT_I8"),
    ]),
    ("DFT_Product_CRA", "UPCCRA.csv", "stg_Product_CRA", [
        ("COM_CODE", "DT_I4"), ("UPC", "DT_I8"), ("DESCRIP", "DT_STR", 100),
        ("SIZE", "DT_STR", 30), ("CASE_PACK", "DT_I4"), ("NITEM", "DT_I8"),
    ]),
    ("DFT_Store", "DEMO.csv", "stg_Store", [
        ("STORE", "DT_STR", 10), ("NAME", "DT_STR", 60), ("CITY", "DT_STR", 50),
        ("ZIP", "DT_STR", 10), ("ZONE", "DT_STR", 10), ("URBAN", "DT_STR", 10),
        ("WEEKVOL", "DT_STR", 20), ("INCOME", "DT_STR", 20),
        ("EDUC", "DT_STR", 20), ("POVERTY", "DT_STR", 20),
        ("HSIZEAVG", "DT_STR", 20), ("ETHNIC", "DT_STR", 20),
        ("DENSITY", "DT_STR", 20), ("AGE9", "DT_STR", 20),
        ("AGE60", "DT_STR", 20), ("WORKWOM", "DT_STR", 20),
        ("PRICLOW", "DT_STR", 10), ("PRICMED", "DT_STR", 10),
        ("PRICHIGH", "DT_STR", 10),
    ]),
]


# ================================================================
# PACKAGE 1: Extract to Staging (9 Data Flow Tasks)
# ================================================================
def generate_package1():
    pkg_guid = new_guid()
    staging_conn_guid = new_guid()
    
    # Build flat file connection managers
    ff_conns = []
    for src in CSV_SOURCES:
        ff_conns.append({
            "name": f"FF_{src[0]}",
            "guid": new_guid(),
            "file": flat_file_conn(src[1]),
            "columns": src[3],
        })
    
    # Build connection manager XML
    conn_mgrs = f'''
    <DTS:ConnectionManager
      DTS:refId="Package.ConnectionManagers[OLE_Staging]"
      DTS:CreationName="OLEDB"
      DTS:DTSID="{staging_conn_guid}"
      DTS:ObjectName="OLE_Staging">
      <DTS:ObjectData>
        <DTS:ConnectionManager
          DTS:ConnectionString="{escape_xml(oledb_conn(STAGING_DB))}" />
      </DTS:ObjectData>
    </DTS:ConnectionManager>'''
    
    for fc in ff_conns:
        cols_xml = ""
        for col in fc["columns"]:
            col_name = col[0]
            col_type = col[1]
            col_len = col[2] if len(col) > 2 else 0
            cols_xml += f'''
              <DTS:FlatFileColumn
                DTS:ColumnType="Delimited"
                DTS:ColumnDelimiter="_x002C_"
                DTS:DataType="{col_type}"
                {"DTS:MaximumWidth=&quot;" + str(col_len) + "&quot;" if col_len > 0 else ""}
                DTS:ObjectName="{col_name}"
                DTS:DTSID="{new_guid()}" />'''
        
        # Last column uses newline delimiter
        cols_xml_lines = cols_xml.strip().rsplit('DTS:ColumnDelimiter="_x002C_"', 1)
        cols_xml = 'DTS:ColumnDelimiter="_x002C_"'.join(cols_xml_lines[:-1]) + \
                   'DTS:ColumnDelimiter="_x000D__x000A_"' + cols_xml_lines[-1] if len(cols_xml_lines) > 1 else cols_xml

        conn_mgrs += f'''
    <DTS:ConnectionManager
      DTS:refId="Package.ConnectionManagers[{fc['name']}]"
      DTS:CreationName="FLATFILE"
      DTS:DTSID="{fc['guid']}"
      DTS:ObjectName="{fc['name']}">
      <DTS:ObjectData>
        <DTS:ConnectionManager
          DTS:Format="Delimited"
          DTS:LocaleID="1033"
          DTS:HeaderRowDelimiter="_x000D__x000A_"
          DTS:ColumnNamesInFirstDataRow="True"
          DTS:RowDelimiter=""
          DTS:TextQualifier="_x003C_none_x003E_"
          DTS:CodePage="1252"
          DTS:ConnectionString="{escape_xml(fc['file'])}">
          <DTS:FlatFileColumns>{cols_xml}
          </DTS:FlatFileColumns>
        </DTS:ConnectionManager>
      </DTS:ObjectData>
    </DTS:ConnectionManager>'''

    # Build Data Flow Tasks
    executables = ""
    prev_task = None
    precedence = ""
    
    for i, src in enumerate(CSV_SOURCES):
        task_guid = new_guid()
        task_name = src[0]
        
        executables += f'''
    <DTS:Executable
      DTS:refId="Package\\{task_name}"
      DTS:CreationName="Microsoft.Pipeline"
      DTS:DTSID="{task_guid}"
      DTS:ExecutableType="Microsoft.Pipeline"
      DTS:LocaleID="-1"
      DTS:ObjectName="{task_name}"
      DTS:TaskContact="Performs high-performance data extraction, transformation and loading;Microsoft Corporation;">
      <DTS:Variables />
      <DTS:ObjectData>
        <pipeline version="1">
          <components>
            <component refId="Package\\{task_name}\\FF_Source"
              componentClassID="Microsoft.FlatFileSource"
              name="FF_Source">
              <properties>
                <property name="RetainNulls">false</property>
              </properties>
              <connections>
                <connection refId="Package\\{task_name}\\FF_Source.Connections[FlatFileConnection]"
                  connectionManagerID="Package.ConnectionManagers[{ff_conns[i]['name']}]"
                  connectionManagerRefId="Package.ConnectionManagers[{ff_conns[i]['name']}]"
                  name="FlatFileConnection" />
              </connections>
              <outputs>
                <output refId="Package\\{task_name}\\FF_Source.Outputs[Flat File Source Output]"
                  name="Flat File Source Output">
                  <outputColumns>'''
        
        for col in src[3]:
            col_name = col[0]
            col_type = col[1]
            col_len = col[2] if len(col) > 2 else 0
            executables += f'''
                    <outputColumn refId="Package\\{task_name}\\FF_Source.Outputs[Flat File Source Output].Columns[{col_name}]"
                      dataType="{col_type}"
                      {"length=&quot;" + str(col_len) + "&quot;" if col_len > 0 else ""}
                      name="{col_name}" />'''
        
        executables += f'''
                  </outputColumns>
                </output>
              </outputs>
            </component>
            <component refId="Package\\{task_name}\\OLE_Destination"
              componentClassID="Microsoft.OLEDBDestination"
              name="OLE_Destination">
              <properties>
                <property name="OpenRowset">[dbo].[{src[2]}]</property>
                <property name="FastLoadOptions">TABLOCK,CHECK_CONSTRAINTS</property>
                <property name="AccessMode">3</property>
                <property name="FastLoadKeepIdentity">false</property>
                <property name="FastLoadKeepNulls">false</property>
                <property name="FastLoadMaxInsertCommitSize">2147483647</property>
              </properties>
              <connections>
                <connection refId="Package\\{task_name}\\OLE_Destination.Connections[OleDbConnection]"
                  connectionManagerID="Package.ConnectionManagers[OLE_Staging]"
                  connectionManagerRefId="Package.ConnectionManagers[OLE_Staging]"
                  name="OleDbConnection" />
              </connections>
              <inputs>
                <input refId="Package\\{task_name}\\OLE_Destination.Inputs[OLE DB Destination Input]"
                  name="OLE DB Destination Input">
                  <inputColumns>'''
        
        for col in src[3]:
            col_name = col[0]
            executables += f'''
                    <inputColumn refId="Package\\{task_name}\\OLE_Destination.Inputs[OLE DB Destination Input].Columns[{col_name}]"
                      cachedName="{col_name}"
                      externalMetadataColumnId="Package\\{task_name}\\OLE_Destination.Inputs[OLE DB Destination Input].ExternalColumns[{col_name}]"
                      lineageId="Package\\{task_name}\\FF_Source.Outputs[Flat File Source Output].Columns[{col_name}]" />'''
        
        executables += f'''
                  </inputColumns>
                  <externalMetadataColumns>'''
        
        for col in src[3]:
            col_name = col[0]
            col_type = col[1]
            col_len = col[2] if len(col) > 2 else 0
            executables += f'''
                    <externalMetadataColumn refId="Package\\{task_name}\\OLE_Destination.Inputs[OLE DB Destination Input].ExternalColumns[{col_name}]"
                      dataType="{col_type}"
                      {"length=&quot;" + str(col_len) + "&quot;" if col_len > 0 else ""}
                      name="{col_name}" />'''
        
        executables += f'''
                  </externalMetadataColumns>
                </input>
              </inputs>
            </component>
          </components>
          <paths>
            <path refId="Package\\{task_name}.Paths[Output]"
              endId="Package\\{task_name}\\OLE_Destination.Inputs[OLE DB Destination Input]"
              startId="Package\\{task_name}\\FF_Source.Outputs[Flat File Source Output]"
              name="Output" />
          </paths>
        </pipeline>
      </DTS:ObjectData>
    </DTS:Executable>'''
        
        if prev_task:
            precedence += f'''
    <DTS:PrecedenceConstraint
      DTS:refId="Package.PrecedenceConstraints[{prev_task}_to_{task_name}]"
      DTS:CreationName=""
      DTS:DTSID="{new_guid()}"
      DTS:From="Package\\{prev_task}"
      DTS:To="Package\\{task_name}"
      DTS:ObjectName="{prev_task}_to_{task_name}" />'''
        prev_task = task_name

    xml = f'''<?xml version="1.0"?>
<DTS:Executable xmlns:DTS="www.microsoft.com/SqlServer/Dts"
  DTS:refId="Package"
  DTS:CreationDate="4/6/2026 12:00:00 AM"
  DTS:CreationName="Microsoft.Package"
  DTS:DTSID="{pkg_guid}"
  DTS:ExecutableType="Microsoft.Package"
  DTS:ObjectName="01_Extract_to_Staging"
  DTS:PackageFormatVersion="8"
  DTS:VersionBuild="1"
  DTS:VersionMajor="1">
  <DTS:Property DTS:Name="PackageFormatVersion">8</DTS:Property>
  <DTS:ConnectionManagers>{conn_mgrs}
  </DTS:ConnectionManagers>
  <DTS:Variables />
  <DTS:Executables>{executables}
  </DTS:Executables>
  <DTS:PrecedenceConstraints>{precedence}
  </DTS:PrecedenceConstraints>
</DTS:Executable>'''
    
    return xml


# ================================================================
# PACKAGE 2: Transform Staging (Execute SQL Tasks)
# ================================================================
def generate_package2():
    pkg_guid = new_guid()
    conn_guid = new_guid()
    
    # Read the transform SQL and split into logical steps
    sql_path = os.path.join(SQL_DIR, "04_transform_staging.sql")
    with open(sql_path, "r") as f:
        full_sql = f.read()
    
    # Split by GO statements into executable blocks
    blocks = []
    current = []
    for line in full_sql.split("\n"):
        stripped = line.strip()
        if stripped.upper() == "GO":
            if current:
                block_sql = "\n".join(current).strip()
                if block_sql and not block_sql.startswith("USE "):
                    blocks.append(block_sql)
                current = []
        else:
            current.append(line)
    if current:
        block_sql = "\n".join(current).strip()
        if block_sql:
            blocks.append(block_sql)
    
    # Group into named tasks
    tasks = [
        ("T1_Add_CATEGORY_CODE_SDR", blocks[0] if len(blocks) > 0 else ""),
        ("T1_Update_CATEGORY_CODE_SDR", blocks[1] if len(blocks) > 1 else ""),
        ("T1_Add_CATEGORY_CODE_CSO", blocks[2] if len(blocks) > 2 else ""),
        ("T1_Update_CATEGORY_CODE_CSO", blocks[3] if len(blocks) > 3 else ""),
        ("T1_Add_CATEGORY_CODE_TPA", blocks[4] if len(blocks) > 4 else ""),
        ("T1_Update_CATEGORY_CODE_TPA", blocks[5] if len(blocks) > 5 else ""),
        ("T1_Add_CATEGORY_CODE_CRA", blocks[6] if len(blocks) > 6 else ""),
        ("T1_Update_CATEGORY_CODE_CRA", blocks[7] if len(blocks) > 7 else ""),
    ]
    # Remaining blocks
    for i, b in enumerate(blocks[8:], start=8):
        # Try to find a comment line for the name
        first_line = b.split("\n")[0].strip()
        if first_line.startswith("--"):
            name = first_line.lstrip("- ").replace(" ", "_")[:40]
        elif first_line.startswith("PRINT"):
            name = f"Print_Step_{i}"
        else:
            name = f"SQL_Step_{i}"
        tasks.append((name.replace("'","").replace('"',''), b))
    
    executables = ""
    prev_task = None
    precedence = ""
    
    for task_name, sql_text in tasks:
        if not sql_text.strip():
            continue
        task_guid = new_guid()
        safe_name = task_name.replace("&", "and").replace("<", "lt").replace(">", "gt")
        
        executables += f'''
    <DTS:Executable
      DTS:refId="Package\\{safe_name}"
      DTS:CreationName="Microsoft.ExecuteSQLTask"
      DTS:DTSID="{task_guid}"
      DTS:ExecutableType="Microsoft.ExecuteSQLTask"
      DTS:ObjectName="{safe_name}">
      <DTS:Variables />
      <DTS:ObjectData>
        <SQLTask:SqlTaskData
          xmlns:SQLTask="www.microsoft.com/sqlserver/dts/tasks/sqltask"
          SQLTask:Connection="OLE_Staging"
          SQLTask:SqlStatementSource="{escape_xml(sql_text)}" />
      </DTS:ObjectData>
    </DTS:Executable>'''
        
        if prev_task:
            precedence += f'''
    <DTS:PrecedenceConstraint
      DTS:refId="Package.PrecedenceConstraints[{prev_task}_to_{safe_name}]"
      DTS:CreationName=""
      DTS:DTSID="{new_guid()}"
      DTS:From="Package\\{prev_task}"
      DTS:To="Package\\{safe_name}"
      DTS:ObjectName="{prev_task}_to_{safe_name}" />'''
        prev_task = safe_name

    xml = f'''<?xml version="1.0"?>
<DTS:Executable xmlns:DTS="www.microsoft.com/SqlServer/Dts"
  DTS:refId="Package"
  DTS:CreationDate="4/6/2026 12:00:00 AM"
  DTS:CreationName="Microsoft.Package"
  DTS:DTSID="{pkg_guid}"
  DTS:ExecutableType="Microsoft.Package"
  DTS:ObjectName="02_Transform_Staging"
  DTS:PackageFormatVersion="8"
  DTS:VersionBuild="1"
  DTS:VersionMajor="1">
  <DTS:Property DTS:Name="PackageFormatVersion">8</DTS:Property>
  <DTS:ConnectionManagers>
    <DTS:ConnectionManager
      DTS:refId="Package.ConnectionManagers[OLE_Staging]"
      DTS:CreationName="OLEDB"
      DTS:DTSID="{conn_guid}"
      DTS:ObjectName="OLE_Staging">
      <DTS:ObjectData>
        <DTS:ConnectionManager
          DTS:ConnectionString="{escape_xml(oledb_conn(STAGING_DB))}" />
      </DTS:ObjectData>
    </DTS:ConnectionManager>
  </DTS:ConnectionManagers>
  <DTS:Variables />
  <DTS:Executables>{executables}
  </DTS:Executables>
  <DTS:PrecedenceConstraints>{precedence}
  </DTS:PrecedenceConstraints>
</DTS:Executable>'''
    
    return xml


# ================================================================
# PACKAGE 3: Load Data Mart (Execute SQL Tasks)
# ================================================================
def generate_package3():
    pkg_guid = new_guid()
    staging_conn_guid = new_guid()
    dw_conn_guid = new_guid()
    
    # Read SQL files for loading
    sql_files = [
        ("05_load_dimensions.sql", "OLE_DW"),
        ("06_load_facts.sql", "OLE_DW"),
        ("07_drop_temp_tables.sql", "OLE_Staging"),
    ]
    
    tasks = []
    for sql_file, conn_name in sql_files:
        sql_path = os.path.join(SQL_DIR, sql_file)
        with open(sql_path, "r") as f:
            full_sql = f.read()
        
        # Split by GO
        blocks = []
        current = []
        for line in full_sql.split("\n"):
            stripped = line.strip()
            if stripped.upper() == "GO":
                if current:
                    block_sql = "\n".join(current).strip()
                    if block_sql and not block_sql.startswith("USE "):
                        blocks.append(block_sql)
                    current = []
            else:
                current.append(line)
        if current:
            block_sql = "\n".join(current).strip()
            if block_sql:
                blocks.append(block_sql)
        
        base = sql_file.replace(".sql", "")
        for i, block in enumerate(blocks):
            first_line = block.split("\n")[0].strip()
            if first_line.startswith("--"):
                name = first_line.lstrip("- ").replace(" ", "_")[:50]
            elif first_line.startswith("PRINT"):
                name = f"{base}_Print_{i}"
            else:
                name = f"{base}_{i}"
            name = name.replace("'","").replace('"','').replace("&","and").replace("(","").replace(")","")
            tasks.append((name, block, conn_name))
    
    executables = ""
    prev_task = None
    precedence = ""
    
    for task_name, sql_text, conn_name in tasks:
        if not sql_text.strip():
            continue
        task_guid = new_guid()
        safe_name = task_name.replace("<","lt").replace(">","gt")
        
        executables += f'''
    <DTS:Executable
      DTS:refId="Package\\{safe_name}"
      DTS:CreationName="Microsoft.ExecuteSQLTask"
      DTS:DTSID="{task_guid}"
      DTS:ExecutableType="Microsoft.ExecuteSQLTask"
      DTS:ObjectName="{safe_name}">
      <DTS:Variables />
      <DTS:ObjectData>
        <SQLTask:SqlTaskData
          xmlns:SQLTask="www.microsoft.com/sqlserver/dts/tasks/sqltask"
          SQLTask:Connection="{conn_name}"
          SQLTask:SqlStatementSource="{escape_xml(sql_text)}" />
      </DTS:ObjectData>
    </DTS:Executable>'''
        
        if prev_task:
            precedence += f'''
    <DTS:PrecedenceConstraint
      DTS:refId="Package.PrecedenceConstraints[{prev_task}_to_{safe_name}]"
      DTS:CreationName=""
      DTS:DTSID="{new_guid()}"
      DTS:From="Package\\{prev_task}"
      DTS:To="Package\\{safe_name}"
      DTS:ObjectName="{prev_task}_to_{safe_name}" />'''
        prev_task = safe_name

    xml = f'''<?xml version="1.0"?>
<DTS:Executable xmlns:DTS="www.microsoft.com/SqlServer/Dts"
  DTS:refId="Package"
  DTS:CreationDate="4/6/2026 12:00:00 AM"
  DTS:CreationName="Microsoft.Package"
  DTS:DTSID="{pkg_guid}"
  DTS:ExecutableType="Microsoft.Package"
  DTS:ObjectName="03_Load_DataMart"
  DTS:PackageFormatVersion="8"
  DTS:VersionBuild="1"
  DTS:VersionMajor="1">
  <DTS:Property DTS:Name="PackageFormatVersion">8</DTS:Property>
  <DTS:ConnectionManagers>
    <DTS:ConnectionManager
      DTS:refId="Package.ConnectionManagers[OLE_Staging]"
      DTS:CreationName="OLEDB"
      DTS:DTSID="{staging_conn_guid}"
      DTS:ObjectName="OLE_Staging">
      <DTS:ObjectData>
        <DTS:ConnectionManager
          DTS:ConnectionString="{escape_xml(oledb_conn(STAGING_DB))}" />
      </DTS:ObjectData>
    </DTS:ConnectionManager>
    <DTS:ConnectionManager
      DTS:refId="Package.ConnectionManagers[OLE_DW]"
      DTS:CreationName="OLEDB"
      DTS:DTSID="{dw_conn_guid}"
      DTS:ObjectName="OLE_DW">
      <DTS:ObjectData>
        <DTS:ConnectionManager
          DTS:ConnectionString="{escape_xml(oledb_conn(DW_DB))}" />
      </DTS:ObjectData>
    </DTS:ConnectionManager>
  </DTS:ConnectionManagers>
  <DTS:Variables />
  <DTS:Executables>{executables}
  </DTS:Executables>
  <DTS:PrecedenceConstraints>{precedence}
  </DTS:PrecedenceConstraints>
</DTS:Executable>'''
    
    return xml


# ================================================================
# Main
# ================================================================
if __name__ == "__main__":
    os.makedirs(SCRIPT_DIR, exist_ok=True)
    
    pkg1 = generate_package1()
    pkg1_path = os.path.join(SCRIPT_DIR, "01_Extract_to_Staging.dtsx")
    with open(pkg1_path, "w", encoding="utf-8") as f:
        f.write(pkg1)
    print(f"  Package 1: {pkg1_path}")
    
    pkg2 = generate_package2()
    pkg2_path = os.path.join(SCRIPT_DIR, "02_Transform_Staging.dtsx")
    with open(pkg2_path, "w", encoding="utf-8") as f:
        f.write(pkg2)
    print(f"  Package 2: {pkg2_path}")
    
    pkg3 = generate_package3()
    pkg3_path = os.path.join(SCRIPT_DIR, "03_Load_DataMart.dtsx")
    with open(pkg3_path, "w", encoding="utf-8") as f:
        f.write(pkg3)
    print(f"  Package 3: {pkg3_path}")
    
    # Also create a README
    readme = f"""# SSIS Packages for DFF Data Warehouse ETL

## Before You Open These Packages

1. **Server:** Update the connection string server name if different from `{SERVER}`
2. **CSV Path:** Update the flat file paths from `{CSV_BASE_PATH}\\` to your actual CSV location
3. **Database names:** Currently set to `{STAGING_DB}` and `{DW_DB}`

## Package Execution Order

1. **Run Scripts 01-03 in SSMS first** (create databases + staging tables + DW tables)
2. Open `01_Extract_to_Staging.dtsx` in Visual Studio (SSDT) and execute
3. Open `02_Transform_Staging.dtsx` and execute
4. Open `03_Load_DataMart.dtsx` and execute
5. Run Script 08 in SSMS to verify BQ queries

## Package Details

| Package | Tasks | Connection | Purpose |
|---------|-------|-----------|---------|
| 01_Extract_to_Staging.dtsx | 9 Data Flow Tasks | Staging DB + 9 Flat File | Load CSVs into staging |
| 02_Transform_Staging.dtsx | Execute SQL Tasks | Staging DB | Clean & transform staging data |
| 03_Load_DataMart.dtsx | Execute SQL Tasks | Staging DB + DW DB | Load dims, fact, drop temps |

## Important Notes

- These packages target **SQL Server 2016** (PackageFormatVersion 8)
- Flat File Sources use **Windows-1252 (CP1252)** encoding
- Column delimiter is **comma**, row delimiter is **CRLF**
- If packages don't open cleanly in SSDT, you can alternatively run the SQL scripts
  directly in SSMS in order: 01 -> 02 -> 03 -> 04 -> 05 -> 06 -> 07 -> 08
"""
    readme_path = os.path.join(SCRIPT_DIR, "README.md")
    with open(readme_path, "w") as f:
        f.write(readme)
    print(f"  README: {readme_path}")
    print("Done! Generated 3 DTSX packages + README.")
