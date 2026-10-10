import DefaultTheme from 'vitepress/theme'
import Comments from '../components/Comments.vue'
import RepoIndex from '../components/RepoIndex.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('Comments', Comments)
    app.component('RepoIndex', RepoIndex)
  },
}