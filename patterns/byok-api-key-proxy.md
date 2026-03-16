---
title: BYOK API Key Proxy Pattern
category: security
tags:
- byok
- encryption
- api-proxy
- aes-gcm
- hkdf
created: 2026-03-10
project: trade-radar
permalink: engineering-playbook/patterns/byok-api-key-proxy
---

# BYOK API Key Proxy Pattern

## 场景

SaaS 平台需要让用户自带 API Key（如 OpenAI、DeepSeek、SerpAPI），调用第三方 AI 服务。用户 Key 不能明文存储，也不能暴露给前端。

## 方案

### 三层架构

```
Frontend → Go API (Key 代理) → AI Service (实际调用 LLM)
```

1. **前端**：用户在 Settings 页输入 Key → 发送到 Go API
2. **Go API**：AES-256-GCM 加密 Key → 存入 DB（JSONB 字段）
3. **调用时**：Go API 解密 Key → 注入 HTTP Header → 转发到 AI Service
4. **AI Service**：从 Header 读取 Key → 动态创建 LLM Client → 调用

### 加密实现

```go
// HKDF 从 JWT_SECRET 派生 AES Key（避免直接使用 JWT_SECRET）
hkdfReader := hkdf.New(sha256.New, []byte(masterSecret),
    []byte("salt-context"), []byte("info-purpose"))
key := make([]byte, 32)
io.ReadFull(hkdfReader, key)

// AES-256-GCM 加密
gcm.Seal(nonce, nonce, plaintext, nil)

// Base64 编码存储
base64.StdEncoding.EncodeToString(ciphertext)
```

### Key 展示

```go
// 返回给前端的掩码版本
func MaskKey(key string) string {
    return key[:3] + "......" + key[len(key)-4:]
}
// "sk-proj-abc...xyzw"
```

### HTTP Header 注入

```go
aiReq.Header.Set("X-OpenAI-Key", decryptedKey)
aiReq.Header.Set("X-DeepSeek-Key", decryptedKey)
aiReq.Header.Set("X-SerpAPI-Key", decryptedKey)
```

### AI Service 端（Python）

```python
def _extract_api_keys(request: Request) -> dict:
    keys = {}
    if v := request.headers.get("x-openai-key"):
        keys["openai"] = v
    if v := request.headers.get("x-deepseek-key"):
        keys["deepseek"] = v
    return keys

# 动态创建 client
client = AsyncOpenAI(api_key=api_keys["openai"])
```

## 注意事项

- HKDF 的 salt 和 info 参数需在代码中固化，换值意味着所有已存储 Key 无法解密
- 更新 Key 时要合并而非覆盖：只更新用户实际修改的 provider
- Go API 必须验证资源归属权后再解密和转发 Key
- AI Service 内部网络通信，Header 中的明文 Key 不经过公网

## 关联

- `relates_to` [[ADR-001-network-isolation]] — API 不直连 traefik-net，Key 不经过公网
- `extends` [[dynamic-config]] — 用户级配置的安全存储扩展