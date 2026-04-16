/**
 * Users页面测试.
 *
 * 测试用户管理页面核心逻辑：格式化、操作处理、状态.
 *
 * Author: FDAS Team
 * Created: 2026-04-15
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import Users from '../Users.vue'
import { nextTick } from 'vue'

// Mock Element Plus icons
vi.mock('@element-plus/icons-vue', () => ({
  Plus: { name: 'Plus', template: '<svg></svg>' },
  UserFilled: { name: 'UserFilled', template: '<svg></svg>' },
  Edit: { name: 'Edit', template: '<svg></svg>' },
  Delete: { name: 'Delete', template: '<svg></svg>' }
}))

// Mock Element Plus - 必须在工厂函数内定义mock对象
vi.mock('element-plus', () => {
  const mockInfo = vi.fn()
  const mockSuccess = vi.fn()
  const mockError = vi.fn()
  return {
    ElMessage: {
      info: mockInfo,
      success: mockSuccess,
      error: mockError
    }
  }
})

// 导入mock后的模块以获取spy引用
import { ElMessage } from 'element-plus'

describe('Users', () => {
  let wrapper: VueWrapper<any>

  // Users组件的完整stubs配置
  const globalConfig = {
    stubs: {
      ElButton: { template: '<button><slot /></button>' },
      ElIcon: { template: '<i><slot /></i>' },
      ElTable: {
        template: '<table class="el-table"><slot /></table>',
        props: ['data']
      },
      ElTableColumn: {
        template: '<td class="el-table-column"><slot name="default" :row="{ username: \'test\', role: \'user\', created_at: \'2026-04-01\', last_login: \'2026-04-10\' }" /></td>',
        props: ['prop', 'label', 'width', 'fixed']
      },
      ElEmpty: { template: '<div class="el-empty"></div>' }
    }
  }

  beforeEach(() => vi.clearAllMocks())
  afterEach(() => wrapper?.unmount())

  describe('格式化函数', () => {
    it('formatDate应正确格式化日期', async () => {
      wrapper = mount(Users, { global: globalConfig })
      await nextTick()
      const vm = wrapper.vm as any
      const result = vm.formatDate('2026-04-01T10:00:00')
      expect(result).toBeTruthy()
      expect(result).toContain('2026')
    })

    it('formatDate应处理空值', async () => {
      wrapper = mount(Users, { global: globalConfig })
      await nextTick()
      const vm = wrapper.vm as any
      expect(vm.formatDate(null)).toBe('')
      expect(vm.formatDate(undefined)).toBe('')
    })
  })

  describe('操作处理', () => {
    it('showCreateDialog应显示提示', async () => {
      wrapper = mount(Users, { global: globalConfig })
      await nextTick()
      const vm = wrapper.vm as any
      vm.showCreateDialog()
      expect(ElMessage.info).toHaveBeenCalledWith('创建用户功能开发中')
    })

    it('editUser应显示提示', async () => {
      wrapper = mount(Users, { global: globalConfig })
      await nextTick()
      const vm = wrapper.vm as any
      vm.editUser({ username: 'test' })
      expect(ElMessage.info).toHaveBeenCalledWith('编辑用户功能开发中')
    })

    it('deleteUser应显示提示', async () => {
      wrapper = mount(Users, { global: globalConfig })
      await nextTick()
      const vm = wrapper.vm as any
      vm.deleteUser({ username: 'test' })
      expect(ElMessage.info).toHaveBeenCalledWith('删除用户功能开发中')
    })
  })

  describe('用户数据', () => {
    it('挂载后应加载模拟用户数据', async () => {
      wrapper = mount(Users, { global: globalConfig })
      await nextTick()
      const vm = wrapper.vm as any
      expect(vm.users.length).toBe(2)
      expect(vm.users[0].username).toBe('admin')
      expect(vm.users[1].username).toBe('user1')
    })

    it('应包含admin和user角色', async () => {
      wrapper = mount(Users, { global: globalConfig })
      await nextTick()
      const vm = wrapper.vm as any
      expect(vm.users.find(u => u.role === 'admin')).toBeTruthy()
      expect(vm.users.find(u => u.role === 'user')).toBeTruthy()
    })
  })

  describe('状态管理', () => {
    it('初始loading应为false', async () => {
      wrapper = mount(Users, { global: globalConfig })
      await nextTick()
      const vm = wrapper.vm as any
      expect(vm.loading).toBe(false)
    })
  })

  describe('页面结构', () => {
    it('应该渲染users-page', () => {
      wrapper = mount(Users, { global: globalConfig })
      expect(wrapper.find('.users-page').exists()).toBe(true)
    })
  })
})