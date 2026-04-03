# FDAS 权限设计文档

> 金融数据抓取与分析系统 - 权限控制设计说明书

**版本**: 1.0
**创建日期**: 2026-04-03
**作者**: FDAS Team

---

## 一、权限模型概述

### 1.1 权限模型选择

**采用RBAC（基于角色的访问控制）模型**

```
┌─────────────────────────────────────────────────────────┐
│                    RBAC权限模型                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│    用户(User) ──── 角色(Role) ──── 权限(Permission)     │
│                                                         │
│    ┌──────┐       ┌──────┐       ┌──────────────┐      │
│    │ admin│ ────> │ admin│ ────> │ 全部权限      │      │
│    └──────┘       └──────┘       └──────────────┘      │
│                                                         │
│    ┌──────┐       ┌──────┐       ┌──────────────┐      │
│    │ user │ ────> │ user │ ────> │ 数据分析查看  │      │
│    └──────┘       └──────┘       └──────────────┘      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 1.2 角色定义

| 角色 | 标识符 | 说明 | 预估人数 |
|------|--------|------|---------|
| **系统管理员** | `admin` | 拥有全部权限，可管理用户、配置、数据 | 1-3人 |
| **普通用户** | `user` | 仅可查看数据分析图表，无法管理配置 | 多人 |

### 1.3 权限控制策略

**前后端双重控制**：

| 层级 | 控制方式 | 目的 |
|------|---------|------|
| **前端** | Vue Router守卫 | 用户体验优化，菜单动态显示 |
| **后端** | FastAPI Depends | 安全保障，拒绝未授权请求 |

---

## 二、角色权限矩阵

### 2.1 功能权限矩阵

| 功能模块 | admin | user | 实现位置 |
|---------|-------|------|---------|
| **数据分析** |
| 查看K线/均线/MACD图 | ✅ | ✅ | FXData.vue |
| 切换时间范围 | ✅ | ✅ | FXData.vue |
| **数据管理** |
| 查看数据源配置 | ✅ | ❌ | DataSource.vue |
| 修改数据源配置 | ✅ | ❌ | DataSource.vue |
| 查看采集任务 | ✅ | ❌ | Collection.vue |
| 创建/启停采集任务 | ✅ | ❌ | Collection.vue |
| **系统管理** |
| 查看用户列表 | ✅ | ❌ | Users.vue |
| 创建/修改/删除用户 | ✅ | ❌ | Users.vue |
| 分配用户角色 | ✅ | ❌ | Users.vue |
| 查看系统日志 | ✅ | ❌ | Logs.vue |
| **个人功能** |
| 登录/登出 | ✅ | ✅ | Login.vue |
| 修改密码（第二阶段） | ✅ | ✅ | Profile.vue |

### 2.2 API权限矩阵

| API端点 | 方法 | admin | user | 权限检查 |
|---------|------|-------|------|---------|
| `/api/v1/auth/login` | POST | ✅ | ✅ | 无需认证 |
| `/api/v1/auth/logout` | POST | ✅ | ✅ | 需登录 |
| `/api/v1/auth/me` | GET | ✅ | ✅ | 需登录 |
| `/api/v1/fx/data` | GET | ✅ | ✅ | 需登录 |
| `/api/v1/fx/indicators` | GET | ✅ | ✅ | 需登录 |
| `/api/v1/datasource` | GET | ✅ | ❌ | 需admin |
| `/api/v1/datasource/{id}` | PUT | ✅ | ❌ | 需admin |
| `/api/v1/collection` | GET | ✅ | ❌ | 需admin |
| `/api/v1/collection` | POST | ✅ | ❌ | 需admin |
| `/api/v1/collection/{id}/status` | PUT | ✅ | ❌ | 需admin |
| `/api/v1/users` | GET | ✅ | ❌ | 需admin |
| `/api/v1/users` | POST | ✅ | ❌ | 需admin |
| `/api/v1/users/{id}` | PUT | ✅ | ❌ | 需admin |
| `/api/v1/users/{id}` | DELETE | ✅ | ❌ | 需admin |
| `/api/v1/system/logs` | GET | ✅ | ❌ | 需admin |

### 2.3 菜单权限矩阵

| 菜单项 | 路由 | admin | user | 菜单父节点 |
|--------|------|-------|------|-----------|
| **数据分析** | /fx-data | ✅ | ✅ | 一级菜单 |
| **数据管理** | - | ✅ | ❌ | 一级菜单 |
| ├ 数据源管理 | /datasource | ✅ | ❌ | 二级菜单 |
| └ 采集任务 | /collection | ✅ | ❌ | 二级菜单 |
| **系统管理** | - | ✅ | ❌ | 一级菜单 |
| ├ 用户管理 | /users | ✅ | ❌ | 二级菜单 |
| └ 系统日志 | /logs | ✅ | ❌ | 二级菜单 |

---

## 三、Session认证设计

### 3.1 Session存储方案

**PostgreSQL服务端存储**

```
┌─────────────────────────────────────────────────────────┐
│                  Session认证流程                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 登录请求                                            │
│     ┌───────┐      ┌───────┐      ┌───────────┐       │
│     │ 用户  │ ───> │验证密码│ ───> │创建Session│       │
│     └───────┘      └───────┘      └───────────┘       │
│                                         │               │
│                                         v               │
│                                  ┌──────────────┐      │
│                                  │ PostgreSQL   │      │
│                                  │ sessions表   │      │
│                                  └──────────────┘      │
│                                                         │
│  2. Cookie返回                                          │
│     ┌───────────────┐                                  │
│     │ Set-Cookie:   │                                  │
│     │ session_id=xxx│                                  │
│     │ HttpOnly      │                                  │
│     │ Secure        │                                  │
│     │ SameSite=Strict│                                 │
│     └───────────────┘                                  │
│                                                         │
│  3. 后续请求                                            │
│     ┌───────┐      ┌───────────┐      ┌───────┐       │
│     │Cookie │ ───> │查询Session│ ───> │返回用户│       │
│     └───────┘      └───────────┘      └───────┘       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Session数据结构

```sql
-- sessions表结构
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_data JSONB NOT NULL,  -- Session数据（JSON格式）
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL  -- 过期时间
);
```

**session_data字段内容**：

```json
{
    "user_id": "uuid-string",
    "username": "admin",
    "role": "admin",
    "login_time": "2026-04-03T14:30:00Z",
    "ip_address": "192.168.1.100"
}
```

### 3.3 Session安全配置

| 配置项 | 值 | 说明 |
|--------|-----|------|
| **Session有效期** | 24小时 | expires_at = created_at + 24h |
| **Cookie属性** | HttpOnly | 防止XSS攻击读取Cookie |
| | Secure | 仅HTTPS传输（生产环境） |
| | SameSite=Strict | 防止CSRF攻击 |
| **Session清理** | 定时任务 | 每小时清理过期Session |

### 3.4 Session认证实现

```python
# backend/app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Request, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session
from app.models.user import User


class SessionManager:
    """
    Session管理器.

    负责Session的创建、查询、删除等操作.
    """

    SESSION_EXPIRE_HOURS = 24  # Session有效期（小时）

    async def create_session(
        self,
        db: AsyncSession,
        user: User,
        request: Request,
    ) -> str:
        """
        创建Session.

        Args:
            db: 数据库会话
            user: 用户对象
            request: 请求对象

        Returns:
            str: Session ID
        """
        expires_at = datetime.utcnow() + timedelta(hours=self.SESSION_EXPIRE_HOURS)

        session = Session(
            user_id=user.id,
            session_data={
                "user_id": str(user.id),
                "username": user.username,
                "role": user.role,
                "login_time": datetime.utcnow().isoformat(),
                "ip_address": request.client.host,
            },
            expires_at=expires_at,
        )

        db.add(session)
        await db.commit()
        await db.refresh(session)

        return str(session.id)

    async def get_session(
        self,
        db: AsyncSession,
        session_id: str,
    ) -> Optional[Session]:
        """
        获取Session.

        Args:
            db: 数据库会话
            session_id: Session ID

        Returns:
            Optional[Session]: Session对象，不存在或已过期返回None
        """
        result = await db.execute(
            select(Session).where(
                Session.id == UUID(session_id),
                Session.expires_at > datetime.utcnow(),
            )
        )
        return result.scalar_one_or_none()

    async def delete_session(
        self,
        db: AsyncSession,
        session_id: str,
    ) -> None:
        """
        删除Session（登出）.

        Args:
            db: 数据库会话
            session_id: Session ID
        """
        result = await db.execute(
            select(Session).where(Session.id == UUID(session_id))
        )
        session = result.scalar_one_or_none()
        if session:
            await db.delete(session)
            await db.commit()


# 全局Session管理器
session_manager = SessionManager()


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    获取当前登录用户.

    从Cookie中读取Session ID，查询数据库获取用户信息.

    Args:
        request: 请求对象
        db: 数据库会话

    Returns:
        User: 当前登录用户

    Raises:
        HTTPException: 401未认证
    """
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="未登录")

    session = await session_manager.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=401, detail="Session已过期")

    # 从session_data中获取用户信息
    user_id = session.session_data.get("user_id")

    result = await db.execute(
        select(User).where(User.id == UUID(user_id))
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user
```

### 3.5 登录API实现

```python
# backend/app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import session_manager, get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.common import Response
from app.services.auth_service import verify_password

router = APIRouter()


@router.post("/login", response_model=Response)
async def login(
    request: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """
    用户登录.

    Args:
        request: 登录请求（用户名、密码）
        response: FastAPI Response对象
        db: 数据库会话

    Returns:
        Response: 登录结果

    Raises:
        HTTPException: 401用户名或密码错误
    """
    # 查询用户
    result = await db.execute(
        select(User).where(User.username == request.username)
    )
    user = result.scalar_one_or_none()

    # 验证用户和密码
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 创建Session
    session_id = await session_manager.create_session(db, user, request)

    # 设置Cookie
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        secure=True,  # 生产环境启用
        samesite="strict",
        max_age=24 * 60 * 60,  # 24小时
    )

    return Response(
        success=True,
        data={"user": {"id": str(user.id), "username": user.username, "role": user.role}},
        message="登录成功",
    )


@router.post("/logout", response_model=Response)
async def logout(
    response: Response,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    用户登出.

    Args:
        response: FastAPI Response对象
        request: 请求对象
        db: 数据库会话

    Returns:
        Response: 登出结果
    """
    session_id = request.cookies.get("session_id")
    if session_id:
        await session_manager.delete_session(db, session_id)

    # 清除Cookie
    response.delete_cookie("session_id")

    return Response(success=True, message="登出成功")


@router.get("/me", response_model=Response)
async def get_me(
    current_user: User = Depends(get_current_user),
):
    """
    获取当前用户信息.

    Args:
        current_user: 当前登录用户

    Returns:
        Response: 用户信息
    """
    return Response(
        success=True,
        data={
            "user": {
                "id": str(current_user.id),
                "username": current_user.username,
                "role": current_user.role,
            }
        },
    )
```

---

## 四、后端权限控制

### 4.1 权限依赖注入

```python
# backend/app/core/deps.py
from fastapi import Depends, HTTPException
from app.core.security import get_current_user
from app.models.user import User


async def require_login(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    要求登录的依赖注入.

    用于需要登录才能访问的API.

    Args:
        current_user: 当前登录用户

    Returns:
        User: 当前用户
    """
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    要求admin权限的依赖注入.

    用于仅admin可访问的API.

    Args:
        current_user: 当前登录用户

    Returns:
        User: admin用户

    Raises:
        HTTPException: 403权限不足
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user
```

### 4.2 API权限使用示例

```python
# backend/app/api/v1/users.py
from fastapi import APIRouter, Depends
from app.core.deps import require_admin
from app.models.user import User

router = APIRouter()


@router.get("/")
async def list_users(
    admin: User = Depends(require_admin),  # 仅admin可访问
):
    """
    获取用户列表.

    仅admin可访问.
    """
    # 查询用户列表...
    pass


@router.post("/")
async def create_user(
    admin: User = Depends(require_admin),  # 仅admin可访问
):
    """
    创建用户.

    仅admin可访问.
    """
    # 创建用户...
    pass


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    admin: User = Depends(require_admin),  # 仅admin可访问
):
    """
    删除用户.

    仅admin可访问.
    """
    # 删除用户...
    pass
```

```python
# backend/app/api/v1/fx_data.py
from fastapi import APIRouter, Depends
from app.core.deps import require_login
from app.models.user import User

router = APIRouter()


@router.get("/data")
async def get_fx_data(
    current_user: User = Depends(require_login),  # 登录即可访问
):
    """
    获取汇率数据.

    登录用户均可访问.
    """
    # 查询汇率数据...
    pass
```

### 4.3 全局异常处理

```python
# backend/app/core/exceptions.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    HTTP异常统一处理.

    Args:
        request: 请求对象
        exc: HTTP异常

    Returns:
        JSONResponse: 统一格式的错误响应
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "message": get_error_message(exc.status_code),
        },
    )


def get_error_message(status_code: int) -> str:
    """
    获取错误消息.

    Args:
        status_code: HTTP状态码

    Returns:
        str: 错误消息
    """
    messages = {
        401: "未登录或Session已过期",
        403: "权限不足",
        404: "资源不存在",
        500: "服务器内部错误",
    }
    return messages.get(status_code, "请求失败")
```

---

## 五、前端权限控制

### 5.1 路由守卫实现

```javascript
// frontend/src/router/guards.js
import { useAuthStore } from '@/stores/auth'

/**
 * 路由守卫：权限检查.
 *
 * 检查顺序：
 * 1. 是否需要登录
 * 2. 是否需要admin权限
 * 3. 已登录用户访问登录页
 */
export function setupRouterGuards(router) {
  router.beforeEach(async (to, from, next) => {
    const authStore = useAuthStore()

    // 尝试获取用户信息（如果未加载）
    if (!authStore.user && authStore.isLoggedIn) {
      await authStore.fetchUser()
    }

    // 1. 检查是否需要登录
    if (to.meta.requiresAuth && !authStore.isLoggedIn) {
      next({
        path: '/login',
        query: { redirect: to.fullPath },  // 保存原目标路径
      })
      return
    }

    // 2. 检查是否需要admin权限
    if (to.meta.requiresAdmin && authStore.user?.role !== 'admin') {
      next('/')  // 跳转首页
      return
    }

    // 3. 已登录用户访问登录页
    if (to.path === '/login' && authStore.isLoggedIn) {
      next('/')
      return
    }

    next()
  })
}
```

### 5.2 路由配置

```javascript
// frontend/src/router/routes.js

/**
 * 路由配置.
 *
 * meta字段说明：
 * - requiresAuth: 是否需要登录
 * - requiresAdmin: 是否需要admin权限
 * - title: 页面标题
 */
export const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: {
      requiresAuth: false,
      title: '登录',
    },
  },
  {
    path: '/',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: {
      requiresAuth: true,
      title: '首页',
    },
  },
  {
    path: '/fx-data',
    name: 'FXData',
    component: () => import('@/views/FXData.vue'),
    meta: {
      requiresAuth: true,  // 需要登录
      requiresAdmin: false,  // 不需要admin
      title: '数据分析',
    },
  },
  {
    path: '/datasource',
    name: 'DataSource',
    component: () => import('@/views/DataSource.vue'),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,  // 需要admin
      title: '数据源管理',
    },
  },
  {
    path: '/collection',
    name: 'Collection',
    component: () => import('@/views/Collection.vue'),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,  // 需要admin
      title: '采集任务',
    },
  },
  {
    path: '/users',
    name: 'Users',
    component: () => import('@/views/Users.vue'),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,  // 需要admin
      title: '用户管理',
    },
  },
  {
    path: '/logs',
    name: 'Logs',
    component: () => import('@/views/Logs.vue'),
    meta: {
      requiresAuth: true,
      requiresAdmin: true,  // 需要admin
      title: '系统日志',
    },
  },
]
```

### 5.3 菜单动态显示

```vue
<!-- frontend/src/components/Sidebar.vue -->
<template>
  <el-menu :default-active="activeMenu" router>
    <el-menu-item index="/fx-data" v-if="showMenuItem('fx-data')">
      <el-icon><TrendCharts /></el-icon>
      <span>数据分析</span>
    </el-menu-item>

    <el-sub-menu index="data-management" v-if="isAdmin">
      <template #title>
        <el-icon><DataAnalysis /></el-icon>
        <span>数据管理</span>
      </template>
      <el-menu-item index="/datasource">数据源管理</el-menu-item>
      <el-menu-item index="/collection">采集任务</el-menu-item>
    </el-sub-menu>

    <el-sub-menu index="system-management" v-if="isAdmin">
      <template #title>
        <el-icon><Setting /></el-icon>
        <span>系统管理</span>
      </template>
      <el-menu-item index="/users">用户管理</el-menu-item>
      <el-menu-item index="/logs">系统日志</el-menu-item>
    </el-sub-menu>
  </el-menu>
</template>

<script setup>
/**
 * 侧边栏菜单组件.
 *
 * 根据用户角色动态显示菜单项.
 */
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { TrendCharts, DataAnalysis, Setting } from '@element-plus/icons-vue'

const route = useRoute()
const authStore = useAuthStore()

// 当前激活菜单
const activeMenu = computed(() => route.path)

// 是否是admin
const isAdmin = computed(() => authStore.user?.role === 'admin')

/**
 * 判断菜单项是否显示.
 *
 * @param {string} menuKey - 菜单标识
 * @returns {boolean} - 是否显示
 */
function showMenuItem(menuKey) {
  // 数据分析：所有用户可见
  if (menuKey === 'fx-data') {
    return true
  }
  // 其他菜单：仅admin可见
  return isAdmin.value
}
</script>
```

### 5.4 权限状态管理

```javascript
// frontend/src/stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/index'

export const useAuthStore = defineStore('auth', () => {
  // 用户信息
  const user = ref(null)

  // 是否已登录（检查Cookie中是否有session_id）
  const isLoggedIn = computed(() => {
    // 这里可以检查Cookie，简单起见检查user是否存在
    return user.value !== null
  })

  // 是否是admin
  const isAdmin = computed(() => user.value?.role === 'admin')

  /**
   * 用户登录.
   *
   * @param {string} username - 用户名
   * @param {string} password - 密码
   * @returns {Promise<boolean>} - 登录是否成功
   */
  async function login(username, password) {
    try {
      const response = await api.post('/api/v1/auth/login', {
        username,
        password,
      })
      if (response.success) {
        user.value = response.data.user
        return true
      }
      return false
    } catch (error) {
      console.error('登录失败:', error)
      return false
    }
  }

  /**
   * 用户登出.
   *
   * @returns {Promise<void>}
   */
  async function logout() {
    try {
      await api.post('/api/v1/auth/logout')
    } catch (error) {
      console.error('登出失败:', error)
    } finally {
      user.value = null
    }
  }

  /**
   * 获取当前用户信息.
   *
   * @returns {Promise<void>}
   */
  async function fetchUser() {
    try {
      const response = await api.get('/api/v1/auth/me')
      if (response.success) {
        user.value = response.data.user
      }
    } catch (error) {
      // 401错误，Session已过期
      user.value = null
    }
  }

  /**
   * 检查权限.
   *
   * @param {string} permission - 权限标识
   * @returns {boolean} - 是否有权限
   */
  function hasPermission(permission) {
    if (!user.value) return false
    if (user.value.role === 'admin') return true

    // user角色权限白名单
    const userPermissions = ['fx-data:view', 'fx-data:indicators']
    return userPermissions.includes(permission)
  }

  return {
    user,
    isLoggedIn,
    isAdmin,
    login,
    logout,
    fetchUser,
    hasPermission,
  }
})
```

### 5.5 权限指令（可选扩展）

```javascript
// frontend/src/directives/permission.js

/**
 * 权限指令.
 *
 * 使用方式：
 * v-permission="'admin'"  - 需要admin角色
 * v-permission="['admin', 'user']"  - 需要admin或user角色
 */
export const permission = {
  mounted(el, binding) {
    const authStore = useAuthStore()
    const value = binding.value

    if (typeof value === 'string') {
      // 单个角色
      if (authStore.user?.role !== value) {
        el.parentNode?.removeChild(el)
      }
    } else if (Array.isArray(value)) {
      // 多个角色
      if (!value.includes(authStore.user?.role)) {
        el.parentNode?.removeChild(el)
      }
    }
  },
}

// 注册指令
// main.js
// app.directive('permission', permission)
```

---

## 六、安全增强措施

### 6.1 密码安全

```python
# backend/app/services/auth_service.py
import bcrypt


def hash_password(password: str) -> str:
    """
    密码加密.

    使用bcrypt算法加密密码.

    Args:
        password: 明文密码

    Returns:
        str: 加密后的密码hash
    """
    salt = bcrypt.gensalt(rounds=12)  # 12轮加密
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """
    密码验证.

    验证密码是否正确.

    Args:
        password: 明文密码
        password_hash: 密码hash

    Returns:
        bool: 密码是否正确
    """
    return bcrypt.checkpw(
        password.encode('utf-8'),
        password_hash.encode('utf-8')
    )
```

### 6.2 Session过期清理

```python
# backend/app/services/session_cleanup_service.py
from datetime import datetime
from sqlalchemy import delete
from app.models.session import Session


async def cleanup_expired_sessions(db: AsyncSession):
    """
    清理过期Session.

    删除数据库中已过期的Session记录.

    Args:
        db: 数据库会话
    """
    await db.execute(
        delete(Session).where(Session.expires_at < datetime.utcnow())
    )
    await db.commit()


# APScheduler定时任务：每小时清理一次
# scheduler.add_job(
#     func=cleanup_expired_sessions,
#     trigger='cron',
#     minute=0,  # 每小时执行
#     id='session_cleanup',
# )
```

### 6.3 登录失败限制（可选扩展）

```python
# backend/app/services/rate_limit_service.py
from datetime import datetime, timedelta
from collections import defaultdict

# 登录失败记录（内存存储，重启后清空）
login_failures = defaultdict(list)

MAX_LOGIN_ATTEMPTS = 5  # 最大尝试次数
LOCKOUT_DURATION = 15 * 60  # 锁定时长（秒）


def is_account_locked(username: str) -> bool:
    """
    检查账户是否被锁定.

    Args:
        username: 用户名

    Returns:
        bool: 是否被锁定
    """
    failures = login_failures[username]
    now = datetime.utcnow()

    # 过滤掉过期的失败记录
    failures = [
        t for t in failures
        if now - t < timedelta(seconds=LOCKOUT_DURATION)
    ]
    login_failures[username] = failures

    return len(failures) >= MAX_LOGIN_ATTEMPTS


def record_login_failure(username: str):
    """
    记录登录失败.

    Args:
        username: 用户名
    """
    login_failures[username].append(datetime.utcnow())


def clear_login_failures(username: str):
    """
    清除登录失败记录.

    Args:
        username: 用户名
    """
    login_failures[username] = []
```

---

## 七、权限测试用例

### 7.1 后端权限测试

```python
# backend/tests/test_permission.py
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestAuthPermission:
    """认证权限测试."""

    def test_login_success(self):
        """测试登录成功."""
        response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "admin123",
        })
        assert response.status_code == 200
        assert "session_id" in response.cookies

    def test_login_wrong_password(self):
        """测试密码错误."""
        response = client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "wrong_password",
        })
        assert response.status_code == 401

    def test_access_protected_api_without_login(self):
        """测试未登录访问受保护API."""
        response = client.get("/api/v1/fx/data")
        assert response.status_code == 401


class TestAdminPermission:
    """Admin权限测试."""

    @pytest.fixture
    def admin_client(self):
        """创建已登录admin的客户端."""
        client.post("/api/v1/auth/login", json={
            "username": "admin",
            "password": "admin123",
        })
        return client

    @pytest.fixture
    def user_client(self):
        """创建已登录user的客户端."""
        client.post("/api/v1/auth/login", json={
            "username": "test_user",
            "password": "user123",
        })
        return client

    def test_admin_access_users_list(self, admin_client):
        """测试admin访问用户列表."""
        response = admin_client.get("/api/v1/users")
        assert response.status_code == 200

    def test_user_access_users_list_forbidden(self, user_client):
        """测试user访问用户列表被拒绝."""
        response = user_client.get("/api/v1/users")
        assert response.status_code == 403

    def test_admin_access_fx_data(self, admin_client):
        """测试admin访问汇率数据."""
        response = admin_client.get("/api/v1/fx/data")
        assert response.status_code == 200

    def test_user_access_fx_data(self, user_client):
        """测试user访问汇率数据."""
        response = user_client.get("/api/v1/fx/data")
        assert response.status_code == 200
```

### 7.2 前端权限测试

```javascript
// frontend/tests/components/Sidebar.test.js
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Sidebar from '@/components/Sidebar.vue'
import { useAuthStore } from '@/stores/auth'

describe('Sidebar', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('admin用户显示所有菜单', () => {
    const authStore = useAuthStore()
    authStore.user = { username: 'admin', role: 'admin' }

    const wrapper = mount(Sidebar)
    expect(wrapper.find('[index="/fx-data"]').exists()).toBe(true)
    expect(wrapper.find('[index="data-management"]').exists()).toBe(true)
    expect(wrapper.find('[index="system-management"]').exists()).toBe(true)
  })

  it('user用户仅显示数据分析菜单', () => {
    const authStore = useAuthStore()
    authStore.user = { username: 'test', role: 'user' }

    const wrapper = mount(Sidebar)
    expect(wrapper.find('[index="/fx-data"]').exists()).toBe(true)
    expect(wrapper.find('[index="data-management"]').exists()).toBe(false)
    expect(wrapper.find('[index="system-management"]').exists()).toBe(false)
  })
})
```

---

## 八、附录

### 8.1 权限检查流程图

```
┌─────────────────────────────────────────────────────────────┐
│                     权限检查流程                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  前端请求 ───> 路由守卫 ───> 后端API ───> 权限依赖 ───> 业务 │
│      │            │            │             │            │
│      │            │            │             │            │
│      v            v            v             v            │
│   检查Cookie   检查meta    检查Session   检查角色          │
│   session_id   requiresAuth  有效期       require_admin    │
│      │            │            │             │            │
│      │            │            │             │            │
│      v            v            v             v            │
│   无Cookie ─> 重定向登录   Session过期 ─> 401错误         │
│   有Cookie ─> 继续检查    Session有效 ─> 检查角色          │
│                                            │               │
│                                            v               │
│                                    角色不匹配 ─> 403错误   │
│                                    角色匹配 ─> 执行业务    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 错误码说明

| HTTP状态码 | 说明 | 前端处理 |
|-----------|------|---------|
| **401** | 未登录或Session已过期 | 重定向到登录页 |
| **403** | 权限不足 | 显示错误提示 |
| **404** | 资源不存在 | 显示404页面 |
| **500** | 服务器内部错误 | 显示错误提示 |

### 8.3 相关文档

- [PRD.md](PRD.md) - 需求设计文档
- [ARCHITECTURE.md](ARCHITECTURE.md) - 技术架构文档
- [CODE_STANDARDS.md](CODE_STANDARDS.md) - 代码规范文档
- [PHASE1_DESIGN.md](PHASE1_DESIGN.md) - 第一阶段设计文档