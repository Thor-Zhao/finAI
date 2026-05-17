import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'FinAI 每周金融追踪',
  description: '金融行业每周追踪信息 - 自动化发布',
  base: '/finAI/',
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '文章', link: '/posts/' },
    ],
    sidebar: [
      {
        text: '文章归档',
        items: [
          { text: '示例文章', link: '/posts/sample' },
        ],
      },
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/Thor-Zhao/finAI' },
    ],
  },
})
