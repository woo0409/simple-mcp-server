# MCP Server 开发经验总结

## 项目概述

本项目是一个入门级 MCP Server 示例，使用 Python + FastMCP 框架开发，通过 Docker 部署到远程服务器，支持 SSE (HTTP) 连接方式。

**部署地址**: http://${SERVER_HOST}:8000/sse

---

## 技术选型

| 技术栈 | 选择 | 理由 |
|--------|------|------|
| 语言 | Python 3.12 | 简单易读，生态丰富 |
| 框架 | FastMCP 2.14.5 | 官方推荐，快速开发，支持 SSE |
| 数据库 | PyMySQL | 纯 Python MySQL 客户端，无需 C 依赖 |
| 容器化 | Docker | 易于部署和隔离 |
| 连接方式 | SSE (HTTP) | 支持远程跨网络访问 |

---

## 项目结构

```
mcp-test/
├── mcp_server/
│   └── main.py          # MCP Server 主程序
├── .dockerignore         # Docker 忽略文件
├── .env.example          # 环境变量示例
├── .gitignore            # Git 忽略文件
├── docker-compose.yml    # Docker 编排配置
├── Dockerfile            # Docker 镜像构建
├── requirements.txt      # Python 依赖
└── README.md             # 项目说明
```

---

## 关键开发经验

### 1. FastMCP 正确用法

**错误写法** ❌
```python
mcp = FastMCP(name="server", host="0.0.0.0", port=8000)
mcp.run(mcp.app)  # FastMCP 没有 .app 属性
```

**正确写法** ✅
```python
mcp = FastMCP(name="server")
mcp.run(transport="sse", host="0.0.0.0", port=8000)
```

### 2. f-string 格式化注意事项

在多行 f-string 中，`{:<46}` 这样的格式化语法会导致错误：

**错误** ❌
```python
print(f"║  Host: {host}:{:<46} ║")
```

**正确** ✅
```python
print(f"║  Host: {host}:{port}                                      ║")
# 或者分开格式化
host_str = f"{host}:{port}"
print(f"║  Host: {host_str:<50} ║")
```

### 3. Docker 配置要点

- FastMCP 没有 `/health` 端点，不要配置健康检查
- 使用非 root 用户运行容器
- 暴露端口 8000 供外部访问

### 4. Claude Code vs Claude Desktop 配置差异

**Claude Code** (`.claude.json`):
```json
{
  "mcpServers": {
    "simple-mcp-server": {
      "type": "sse",
      "url": "http://${SERVER_HOST}:8000/sse"
    }
  }
}
```

**Claude Desktop** (`%APPDATA%\Claude\claude.json`):
```json
{
  "mcpServers": {
    "simple-mcp-server": {
      "transport": {
        "type": "sse",
        "url": "http://${SERVER_HOST}:8000/sse"
      }
    }
  }
}
```

### 5. 远程部署流程

```bash
# 1. 本地打包
tar -czf mcp-server.tar.gz mcp_server/ requirements.txt Dockerfile docker-compose.yml ...

# 2. 上传到服务器
scp mcp-server.tar.gz ubuntu@${SERVER_HOST}:/tmp/

# 3. 服务器解压并部署
ssh ubuntu@${SERVER_HOST}
cd ~/mcp-server
tar -xzf /tmp/mcp-server.tar.gz
sudo docker-compose down && sudo docker-compose build && sudo docker-compose up -d

# 4. 验证
sudo docker-compose ps
sudo docker-compose logs -f
curl -s http://localhost:8000/sse
```

### 6. 端口占用处理

```bash
# 查看占用端口的容器
sudo docker ps

# 停止并删除占用容器
sudo docker stop <container_name>
sudo docker rm <container_name>
```

### 7. Docker 容器访问宿主机数据库

当数据库运行在宿主机上时，容器内需要特殊配置才能访问：

**方案 A: 使用 host 网络模式** ✅ 推荐
```yaml
# docker-compose.yml
services:
  mcp-server:
    network_mode: host  # 直接使用宿主机网络
    environment:
      - DB_HOST=localhost  # 可以直接用 localhost
```

**方案 B: 使用 Docker 网关地址**
```yaml
services:
  mcp-server:
    environment:
      - DB_HOST=172.17.0.1  # Linux Docker 默认网关
      # Mac/Windows: host.docker.internal
```

**注意**: 确保数据库监听 `0.0.0.0` 或 `127.0.0.1`，而不是仅监听 `localhost`。

### 8. 数据库查询安全限制

实现只读数据库工具时的安全措施：

```python
def execute_sql_query(sql: str) -> list[dict]:
    # 1. 只允许只读操作
    readonly_keywords = ["SELECT", "SHOW", "DESCRIBE", "DESC", "EXPLAIN"]
    if not any(sql.upper().startswith(kw) for kw in readonly_keywords):
        raise ValueError("只支持只读查询")

    # 2. 拦截危险关键字
    dangerous = ["DROP", "DELETE", "INSERT", "UPDATE", "CREATE"]
    for kw in dangerous:
        if kw in sql.upper():
            raise ValueError(f"不允许使用 {kw}")

    # 3. 自动添加 LIMIT
    if "LIMIT" not in sql.upper():
        sql = f"{sql} LIMIT 100"
```

---

## 工具开发模式

### 基本工具模板

```python
@mcp.tool()
def tool_name(param: type, default: type = default_value) -> return_type:
    """工具描述（会被用作文档）

    Args:
        param: 参数说明

    Returns:
        返回值说明
    """
    # 实现逻辑
    return result
```

### 资源定义模板

```python
@mcp.resource("resource://identifier")
def get_resource() -> str:
    """资源描述"""
    return "资源内容"
```

---

## 常见问题

### Q: MCP Server 启动后立即重启
**A**: 检查日志，常见原因：
- 代码语法错误
- 端口被占用
- 环境变量配置错误

### Q: 无法从外部访问
**A**: 检查：
- Docker 端口映射是否正确 (`ports: - "8000:8000"`)
- 服务器防火墙是否开放 (`sudo ufw status`)
- 服务绑定地址是否为 `0.0.0.0`

### Q: Claude Code 无法连接
**A**: 确认：
- 配置文件位置正确 (`~/.claude.json`)
- 配置格式使用 `"type": "sse"` 而非 `"transport"`
- SSE 端点可访问 (`curl http://server:8000/sse`)

### Q: 数据库连接失败 (Connection refused)
**A**: 常见原因：
- Docker 容器内 `localhost` 无法访问宿主机数据库
- 解决方案：使用 `network_mode: host` 或配置 `DB_HOST=172.17.0.1`
- 检查数据库是否运行：`sudo docker ps | grep mysql`
- 检查数据库监听：`sudo netstat -tlnp | grep 3306`

### Q: SQL 查询返回 "只支持只读查询"
**A**: 这是安全限制，只允许以下操作：
- SELECT 查询
- SHOW 命令
- DESCRIBE 命令
- EXPLAIN 命令

### Q: MCP Server 初始化警告
**A**: `Received request before initialization was complete` 警告：
- 通常在服务刚启动时出现
- 可以忽略，等待几秒后重试即可

---

## 可用工具

### 基础工具

| 工具名 | 描述 | 示例 |
|--------|------|------|
| `get_current_time` | 获取服务器时间 | "现在几点了？" |
| `calculate` | 数学计算 | "123 × 456 等于多少？" |
| `echo` | 回显内容 | "重复三次：你好" |
| `get_server_info` | 服务器信息 | "服务器是什么系统？" |
| `reverse_text` | 反转文本 | "反转：hello" |

### 数据库工具

| 工具名 | 描述 | 参数 | 示例 |
|--------|------|------|------|
| `db_list_tables` | 列出所有表 | 无 | "有哪些表？" |
| `db_describe_table` | 获取表结构 | table_name | "users 表结构？" |
| `db_execute_query` | 执行 SQL 查询 | sql, limit | "查询 users 表" |
| `db_get_row_count` | 获取表行数 | table_name | "users 有多少行？" |
| `db_list_databases` | 列出所有数据库 | 无 | "有哪些数据库？" |

### 查询示例

```sql
-- 基本查询
SELECT * FROM users

-- 条件查询
SELECT * FROM users WHERE name = '张三'

-- 排序分页
SELECT id, name FROM users ORDER BY id DESC LIMIT 5

-- 表结构
DESCRIBE users
```

---

## 管理命令

```bash
# SSH 连接
ssh ubuntu@${SERVER_HOST}

# 进入项目目录
cd ~/mcp-server

# 查看状态
sudo docker-compose ps

# 查看日志
sudo docker-compose logs -f

# 重启服务
sudo docker-compose restart

# 停止服务
sudo docker-compose down

# 重新部署
tar -xzf /tmp/mcp-server.tar.gz && sudo docker-compose build && sudo docker-compose up -d
```

---

## 后续扩展方向

- [x] **添加数据库支持** - 连接 MySQL 提供数据查询工具 ✅ 已完成
- [ ] **文件操作** - 添加读写远程服务器文件的工具
- [ ] **系统监控** - 添加 CPU、内存、磁盘使用率监控
- [ ] **认证鉴权** - 添加 API Key 认证保护服务
- [ ] **日志持久化** - 集成日志收集和分析
- [ ] **多数据库支持** - 支持 PostgreSQL、MongoDB 等
- [ ] **缓存机制** - 添加查询结果缓存提升性能

---

## 参考资料

- [FastMCP 文档](https://gofastmcp.com)
- [MCP 协议规范](https://modelcontextprotocol.io)
- [Docker 官方文档](https://docs.docker.com)
