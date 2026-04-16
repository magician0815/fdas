/**
 * Layout.vue渲染测试.
 *
 * 测试主布局组件的渲染和交互.
 *
 * Author: FDAS Team
 * Created: 2026-04-16
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import Layout from '../Layout.vue'

// Mock Element Plus components
vi.mock('element-plus', () => ({
  ElAside: {
    template: '<aside class="el-aside"><slot /></aside>',
    props: ['width']
  },
  ElContainer: {
    template: '<div class="el-container"><slot /></div>'
  },
  ElHeader: {
    template: '<header class="el-header"><slot /></header>'
  },
  ElMain: {
    template: '<main class="el-main"><slot /></main>'
  }
}))

// Mock child components
vi.mock('../Sidebar.vue', () => ({
  default: {
    template: '<div class="sidebar-mock">Sidebar</div>',
    props: ['collapsed']
  }
}))

vi.mock('../Navbar.vue', () => ({
  default: {
    template: '<div class="navbar-mock">Navbar</div>'
  }
}))

vi.mock('../HelpButton.vue', () => ({
  default: {
    template: '<div class="help-button-mock">HelpButton</div>'
  }
}))

describe('Layout.vue渲染测试', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  describe('页面结构渲染', () => {
    it('应渲染布局容器', () => {
      const wrapper = mount(Layout, {
        global: { stubs: { Sidebar: true, Navbar: true, HelpButton: true, RouterView: true } }
      })
      expect(wrapper.find('.layout-container').exists()).toBe(true)
    })

    it('应渲染侧边栏区域', () => {
      const wrapper = mount(Layout, {
        global: { stubs: { Sidebar: true, Navbar: true, HelpButton: true, RouterView: true } }
      })
      expect(wrapper.find('.sidebar').exists()).toBe(true)
    })

    it('应渲染主容器', () => {
      const wrapper = mount(Layout, {
        global: { stubs: { Sidebar: true, Navbar: true, HelpButton: true, RouterView: true } }
      })
      expect(wrapper.find('.main-container').exists()).toBe(true)
    })

    it('应渲染顶部导航栏区域', () => {
      const wrapper = mount(Layout, {
        global: { stubs: { Sidebar: true, Navbar: true, HelpButton: true, RouterView: true } }
      })
      expect(wrapper.find('.header').exists()).toBe(true)
    })

    it('应渲染主内容区域', () => {
      const wrapper = mount(Layout, {
        global: { stubs: { Sidebar: true, Navbar: true, HelpButton: true, RouterView: true } }
      })
      expect(wrapper.find('.main').exists()).toBe(true)
    })
  })

  describe('侧边栏折叠功能', () => {
    it('初始状态应为展开', () => {
      const wrapper = mount(Layout, {
        global: { stubs: { Sidebar: true, Navbar: true, HelpButton: true, RouterView: true } }
      })
      expect(wrapper.vm.isCollapsed).toBe(false)
    })

    it('展开时侧边栏宽度应为220px', () => {
      const wrapper = mount(Layout, {
        global: { stubs: { Sidebar: true, Navbar: true, HelpButton: true, RouterView: true } }
      })
      expect(wrapper.vm.sidebarWidth).toBe('220px')
    })

    it('折叠时侧边栏宽度应为64px', () => {
      const wrapper = mount(Layout, {
        global: { stubs: { Sidebar: true, Navbar: true, HelpButton: true, RouterView: true } }
      })
      wrapper.vm.toggleSidebar()
      expect(wrapper.vm.sidebarWidth).toBe('64px')
    })

    it('toggleSidebar应切换折叠状态', () => {
      const wrapper = mount(Layout, {
        global: { stubs: { Sidebar: true, Navbar: true, HelpButton: true, RouterView: true } }
      })
      wrapper.vm.toggleSidebar()
      expect(wrapper.vm.isCollapsed).toBe(true)
      wrapper.vm.toggleSidebar()
      expect(wrapper.vm.isCollapsed).toBe(false)
    })
  })

  describe('子组件渲染', () => {
    it('应包含Sidebar组件', () => {
      const wrapper = mount(Layout, {
        global: { stubs: { Navbar: true, HelpButton: true, RouterView: true } }
      })
      expect(wrapper.find('.sidebar-mock').exists()).toBe(true)
    })

    it('应包含Navbar组件', () => {
      const wrapper = mount(Layout, {
        global: { stubs: { Sidebar: true, HelpButton: true, RouterView: true } }
      })
      expect(wrapper.find('.navbar-mock').exists()).toBe(true)
    })

    it('应包含HelpButton组件', () => {
      const wrapper = mount(Layout, {
        global: { stubs: { Sidebar: true, Navbar: true, RouterView: true } }
      })
      expect(wrapper.find('.help-button-mock').exists()).toBe(true)
    })
  })

  describe('组件属性传递', () => {
    it('Sidebar应接收collapsed属性', () => {
      const wrapper = mount(Layout, {
        global: { stubs: { Navbar: true, HelpButton: true, RouterView: true } }
      })
      const sidebar = wrapper.findComponent({ name: 'Sidebar' })
      expect(sidebar.props('collapsed')).toBe(false)
    })
  })
})