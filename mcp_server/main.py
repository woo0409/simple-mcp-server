"""Simple MCP Server - Entry point with SSE support."""

import os
import platform
from datetime import datetime
from typing import Any
from contextlib import contextmanager

import pymysql
from pymysql.cursors import DictCursor
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get server config
server_name = os.getenv("MCP_SERVER_NAME", "simple-mcp-server")
server_host = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
server_port = int(os.getenv("MCP_SERVER_PORT", "8000"))

# Database config
db_config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "mcp_user"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "mcp_db"),
    "charset": os.getenv("DB_CHARSET", "utf8mb4"),
    "autocommit": True
}

# Create MCP Server instance
mcp = FastMCP(name=server_name)


# ============= Database Helper Functions =============

@contextmanager
def get_db_connection():
    """获取数据库连接上下文管理器"""
    conn = pymysql.connect(**db_config)
    try:
        yield conn
    finally:
        conn.close()


def execute_sql_query(sql: str) -> list[dict[str, Any]]:
    """执行 SQL 查询并返回结果

    Args:
        sql: SQL 查询语句

    Returns:
        查询结果列表

    Raises:
        ValueError: 如果 SQL 包含非只读操作
    """
    sql_upper = sql.strip().upper()

    # 只允许只读操作
    readonly_keywords = [
        "SELECT", "SHOW", "DESCRIBE", "DESC", "EXPLAIN", "WITH"
    ]

    if not any(sql_upper.startswith(kw) for kw in readonly_keywords):
        raise ValueError(
            f"只支持只读查询操作 (SELECT, SHOW, DESCRIBE 等)。"
            f"不允许的操作: {sql.split()[0] if sql else 'empty'}"
        )

    # 检查是否包含危险关键字
    dangerous_keywords = [
        "DROP", "DELETE", "INSERT", "UPDATE", "CREATE", "ALTER",
        "TRUNCATE", "GRANT", "REVOKE", "COMMIT", "ROLLBACK"
    ]
    for kw in dangerous_keywords:
        if kw in sql_upper:
            raise ValueError(f"不允许在查询中使用 {kw} 操作")

    with get_db_connection() as conn:
        with conn.cursor(DictCursor) as cursor:
            cursor.execute(sql)
            return cursor.fetchall()


# ============= MCP Tools =============

@mcp.tool()
def get_current_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """获取当前服务器时间

    Args:
        format: 时间格式字符串，默认为 "%Y-%m-%d %H:%M:%S"

    Returns:
        格式化的当前时间字符串
    """
    return datetime.now().strftime(format)


@mcp.tool()
def calculate(operation: str, a: float, b: float) -> float:
    """执行简单的数学计算

    Args:
        operation: 运算类型，支持 "add", "subtract", "multiply", "divide"
        a: 第一个数字
        b: 第二个数字

    Returns:
        计算结果

    Raises:
        ValueError: 当运算类型不支持或除数为零时
    """
    operations = {
        "add": lambda x, y: x + y,
        "subtract": lambda x, y: x - y,
        "multiply": lambda x, y: x * y,
        "divide": lambda x, y: x / y if y != 0 else (_ for _ in ()).throw(ValueError("除数不能为零"))
    }

    if operation not in operations:
        raise ValueError(f"不支持的运算类型: {operation}。支持的类型: {', '.join(operations.keys())}")

    return operations[operation](a, b)


@mcp.tool()
def echo(message: str, repeat: int = 1) -> str:
    """回显输入内容

    Args:
        message: 要回显的消息
        repeat: 重复次数，默认为 1

    Returns:
        回显的消息内容
    """
    if repeat < 1:
        raise ValueError("重复次数必须大于等于 1")

    return " ".join([message] * repeat)


@mcp.tool()
def get_server_info() -> dict[str, Any]:
    """获取服务器基本信息

    Returns:
        包含服务器系统信息的字典
    """
    return {
        "hostname": platform.node(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "server_time": datetime.now().isoformat()
    }


@mcp.tool()
def reverse_text(text: str) -> str:
    """反转输入的文本

    Args:
        text: 要反转的文本

    Returns:
        反转后的文本
    """
    return text[::-1]


# ============= Database Tools =============

@mcp.tool()
def db_list_tables() -> dict[str, Any]:
    """列出数据库中的所有表

    Returns:
        包含表列表和数量的字典
    """
    try:
        tables = execute_sql_query("SHOW TABLES")
        table_names = [list(t.values())[0] for t in tables]
        return {
            "database": db_config["database"],
            "table_count": len(table_names),
            "tables": table_names
        }
    except Exception as e:
        return {"error": str(e), "tables": []}


@mcp.tool()
def db_describe_table(table_name: str) -> dict[str, Any]:
    """获取表结构信息

    Args:
        table_name: 表名

    Returns:
        包含表结构信息的字典
    """
    try:
        columns = execute_sql_query(
            "DESCRIBE `%s`" % table_name
        )

        # 获取表统计信息
        count_result = execute_sql_query(
            "SELECT COUNT(*) as total FROM `%s`" % table_name
        )
        row_count = count_result[0]["total"] if count_result else 0

        return {
            "table": table_name,
            "row_count": row_count,
            "columns": columns
        }
    except Exception as e:
        return {"error": str(e), "table": table_name}


@mcp.tool()
def db_execute_query(sql: str, limit: int = 100) -> dict[str, Any]:
    """执行只读 SQL 查询

    Args:
        sql: SQL 查询语句（只支持 SELECT 等只读操作）
        limit: 最大返回行数，默认 100

    Returns:
        查询结果字典

    Raises:
        ValueError: 如果 SQL 包含非只读操作
    """
    try:
        # 添加 LIMIT 限制（如果 SQL 中没有）
        sql_upper = sql.strip().upper()
        if "LIMIT" not in sql_upper:
            sql = f"{sql.rstrip(';')} LIMIT {limit}"

        results = execute_sql_query(sql)

        return {
            "sql": sql,
            "row_count": len(results),
            "results": results
        }
    except ValueError as e:
        return {"error": str(e), "sql": sql}
    except Exception as e:
        return {"error": f"数据库错误: {str(e)}", "sql": sql}


@mcp.tool()
def db_get_row_count(table_name: str) -> dict[str, Any]:
    """获取表的行数

    Args:
        table_name: 表名

    Returns:
        包含行数信息的字典
    """
    try:
        result = execute_sql_query(
            "SELECT COUNT(*) as total FROM `%s`" % table_name
        )
        return {
            "table": table_name,
            "row_count": result[0]["total"]
        }
    except Exception as e:
        return {"error": str(e), "table": table_name}


@mcp.tool()
def db_list_databases() -> dict[str, Any]:
    """列出所有可访问的数据库

    Returns:
        包含数据库列表的字典
    """
    try:
        # 使用当前连接查询所有数据库
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SHOW DATABASES")
                databases = [row["Database"] for row in cursor.fetchall()]
        return {
            "databases": databases,
            "current": db_config["database"]
        }
    except Exception as e:
        return {"error": str(e), "databases": []}


# ============= Resources =============

@mcp.resource("server://status")
def get_server_status() -> str:
    """服务器状态资源"""
    return f"""
    服务器状态 - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    状态: 运行中
    系统: {platform.system()} {platform.release()}
    """


@mcp.resource("server://tools")
def list_available_tools() -> str:
    """可用工具列表资源"""
    return """
    可用工具列表:

    基础工具:
    - get_current_time: 获取当前服务器时间
    - calculate: 执行数学计算 (add, subtract, multiply, divide)
    - echo: 回显输入内容
    - get_server_info: 获取服务器信息
    - reverse_text: 反转文本

    数据库工具:
    - db_list_tables: 列出所有表
    - db_describe_table: 获取表结构
    - db_execute_query: 执行只读 SQL 查询
    - db_get_row_count: 获取表行数
    - db_list_databases: 列出所有数据库
    """


# ============= Main Entry Point =============

def main():
    """启动 MCP Server"""
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║           Simple MCP Server - SSE Mode                   ║
    ╠═══════════════════════════════════════════════════════════╣
    ║  Name: {server_name:<50} ║
    ║  Host: {server_host}:{server_port}                                      ║
    ║  SSE Endpoint: http://{server_host}:{server_port}/sse              ║
    ║  Message Endpoint: http://{server_host}:{server_port}/messages/     ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Run the MCP server
    mcp.run(transport="sse", host=server_host, port=server_port)


if __name__ == "__main__":
    main()
