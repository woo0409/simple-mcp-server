# Simple MCP Server

一个简单的入门级 MCP Server 示例，支持 SSE (HTTP) 连接方式。

## 功能特性

- 🛠️ 5 个示例工具
- 📡 SSE (HTTP) 连接支持
- 🐳 Docker 容器化部署
- 📝 健康检查

## 可用工具

| 工具名 | 描述 |
|--------|------|
| `get_current_time` | 获取当前服务器时间 |
| `calculate` | 执行数学计算 (add, subtract, multiply, divide) |
| `echo` | 回显输入内容 |
| `get_server_info` | 获取服务器系统信息 |
| `reverse_text` | 反转文本 |

## 快速开始

### 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
python -m mcp_server.main
```

服务将在 http://localhost:8000 启动

### Docker 运行

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## API 端点

| 端点 | 描述 |
|------|------|
| `/sse` | SSE 连接端点 |
| `/messages/` | 消息处理端点 |
| `/health` | 健康检查端点 |

## Claude Desktop 配置

在 Claude Desktop 配置文件中添加（将 `your-server-ip` 替换为实际服务器地址）：

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

**Claude Code 配置** (`~/.claude.json`)：

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

## 环境变量

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `MCP_SERVER_NAME` | simple-mcp-server | 服务器名称 |
| `MCP_SERVER_PORT` | 8000 | 服务端口 |
| `LOG_LEVEL` | INFO | 日志级别 |

## 部署

### 远程服务器部署

将 `your-server-ip` 替换为实际服务器地址：

```bash
# 1. 复制文件到服务器
scp -r . ubuntu@your-server-ip:/home/ubuntu/mcp-server/

# 2. SSH 连接到服务器
ssh ubuntu@your-server-ip

# 3. 进入目录并启动
cd /home/ubuntu/mcp-server
docker-compose up -d

# 4. 检查状态
docker-compose ps
docker-compose logs -f
```

## 测试

```bash
# 健康检查
curl http://localhost:8000/health

# 测试工具调用（通过 MCP 客户端）
# 或使用 Claude Desktop 连接测试
```
