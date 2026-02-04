# Simple MCP Server

一个入门级 MCP Server 示例，使用 Python + FastMCP 框架开发，支持 SSE (HTTP) 连接方式和 MySQL 数据库查询。

## ✨ 功能特性

- 🛠️ **10 个实用工具** - 基础工具 + 数据库查询工具
- 🗄️ **MySQL 数据库支持** - 只读查询，安全限制
- 📡 **SSE (HTTP) 连接** - 支持远程跨网络访问
- 🐳 **Docker 容器化** - 一键部署，易于管理
- 🔒 **安全查询限制** - 防止恶意 SQL 操作

## 📋 可用工具

### 基础工具

| 工具名 | 描述 | 示例 |
|--------|------|------|
| `get_current_time` | 获取当前服务器时间 | "现在几点了？" |
| `calculate` | 数学计算 (加减乘除) | "123 × 456 等于多少？" |
| `echo` | 回显输入内容 | "重复三次：你好" |
| `get_server_info` | 获取服务器系统信息 | "服务器是什么系统？" |
| `reverse_text` | 反转文本 | "反转：hello" |

### 数据库工具

| 工具名 | 描述 | 参数 | 示例 |
|--------|------|------|------|
| `db_list_tables` | 列出所有表 | 无 | "有哪些表？" |
| `db_describe_table` | 获取表结构 | table_name | "users 表结构？" |
| `db_execute_query` | 执行只读 SQL 查询 | sql, limit | "查询 users 表" |
| `db_get_row_count` | 获取表行数 | table_name | "users 有多少行？" |
| `db_list_databases` | 列出所有数据库 | 无 | "有哪些数据库？" |

### SQL 查询示例

```sql
-- 基本查询
SELECT * FROM users

-- 条件查询
SELECT * FROM users WHERE name = '张三'

-- 模糊搜索
SELECT * FROM users WHERE name LIKE '%许%'

-- 排序分页
SELECT id, name FROM users ORDER BY id DESC LIMIT 5

-- 统计
SELECT COUNT(*) as total FROM users
```

---

## 🚀 快速开始

### 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件配置数据库连接信息

# 3. 启动服务
python -m mcp_server.main
```

服务将在 http://localhost:8000 启动

### Docker 运行（推荐）

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart
```

---

## 🔧 配置说明

### 环境变量

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `MCP_SERVER_NAME` | simple-mcp-server | 服务器名称 |
| `MCP_SERVER_PORT` | 8000 | 服务端口 |
| `LOG_LEVEL` | INFO | 日志级别 |

### 数据库环境变量

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `DB_HOST` | localhost | 数据库主机 |
| `DB_PORT` | 3306 | 数据库端口 |
| `DB_USER` | mcp_user | 数据库用户 |
| `DB_PASSWORD` | (必填) | 数据库密码 |
| `DB_NAME` | mcp_db | 数据库名称 |
| `DB_CHARSET` | utf8mb4 | 字符集 |

**注意**：Docker 部署时，数据库配置已包含在 docker-compose.yml 中，无需额外配置。

---

## 🔌 Claude Code 配置

在 `~/.claude.json` 中添加（将 `your-server-ip` 替换为实际服务器地址）：

```json
{
  "mcpServers": {
    "simple-mcp-server": {
      "type": "sse",
      "url": "http://your-server-ip:8000/sse"
    }
  }
}
```

### Claude Desktop 配置

在 `%APPDATA%\Claude\claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "simple-mcp-server": {
      "transport": {
        "type": "sse",
        "url": "http://your-server-ip:8000/sse"
      }
    }
  }
}
```

配置完成后重启 Claude Desktop 即可。

---

## 🌐 远程服务器部署

### 前置要求

- Linux 服务器（Ubuntu 推荐）
- 已安装 Docker 和 Docker Compose
- 已安装 MySQL 8.0+

### 部署步骤

将 `your-server-ip` 替换为实际服务器地址：

```bash
# 1. 本地打包
tar -czf mcp-server.tar.gz mcp_server/ requirements.txt Dockerfile docker-compose.yml .env.example

# 2. 上传到服务器
scp mcp-server.tar.gz ubuntu@your-server-ip:/tmp/

# 3. SSH 连接到服务器
ssh ubuntu@your-server-ip

# 4. 创建目录并解压
mkdir -p ~/mcp-server
cd ~/mcp-server
tar -xzf /tmp/mcp-server.tar.gz

# 5. 启动服务
sudo docker-compose up -d

# 6. 检查状态
sudo docker-compose ps
sudo docker-compose logs -f
```

### 验证部署

```bash
# 检查 SSE 端点
curl -s http://localhost:8000/sse

# 在本地 Claude Code 中测试连接
```

---

## 📊 API 端点

| 端点 | 描述 |
|------|------|
| `/sse` | SSE 连接端点 |
| `/messages/` | 消息处理端点 |

---

## 🔒 安全特性

### SQL 查询安全限制

- ✅ **支持的操作**：SELECT、SHOW、DESCRIBE、EXPLAIN
- ❌ **拒绝的操作**：DROP、DELETE、INSERT、UPDATE、CREATE、ALTER
- 🛡️ **自动保护**：未指定 LIMIT 时自动添加（默认 100 行）

### 示例

```python
# ✅ 允许
db_execute_query("SELECT * FROM users")

# ❌ 拒绝
db_execute_query("DROP TABLE users")  # 错误：不允许使用 DROP
db_execute_query("DELETE FROM users")  # 错误：不允许使用 DELETE
```

---

## 🛠️ 管理命令

```bash
# SSH 连接
ssh ubuntu@your-server-ip

# 进入项目目录
cd ~/mcp-server

# 查看容器状态
sudo docker-compose ps

# 查看日志
sudo docker-compose logs -f

# 重启服务
sudo docker-compose restart

# 停止服务
sudo docker-compose down

# 重新部署
sudo docker-compose down
tar -xzf /tmp/mcp-server.tar.gz
sudo docker-compose build
sudo docker-compose up -d
```

---

## 📖 技术架构

```
┌─────────────────┐         SSE/HTTP          ┌──────────────────┐
│   Claude Code   │ ◄──────────────────────► │  Docker 容器      │
│                  │     端口: 8000           │                  │
└─────────────────┘                          └──────────────────┘
                                                      │
                                                      ▼
                                              ┌──────────────────┐
                                              │   MySQL 数据库    │
                                              └──────────────────┘
```

**工作流程**：
1. Claude Code 通过 SSE 连接到 MCP Server
2. 用户提问时，Claude Code 调用相应的工具
3. MCP Server 执行工具（如查询数据库）
4. 结果返回给 Claude Code 展示给用户

---

## 📂 项目结构

```
mcp-test/
├── mcp_server/
│   ├── __init__.py
│   └── main.py              # MCP Server 主程序
├── .dockerignore              # Docker 忽略文件
├── .env.example               # 环境变量示例
├── .gitignore                 # Git 忽略文件
├── docker-compose.yml         # Docker 编排配置
├── Dockerfile                 # Docker 镜像构建
├── requirements.txt           # Python 依赖
├── CLAUDE.md                  # 开发文档
└── README.md                 # 项目说明
```

---

## 📚 参考资料

- [FastMCP 文档](https://gofastmcp.com)
- [MCP 协议规范](https://modelcontextprotocol.io)
- [Docker 官方文档](https://docs.docker.com)

---

## 📄 License

MIT License
