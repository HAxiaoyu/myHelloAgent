// src/frontend/src/utils/markdown.js
import MarkdownIt from 'markdown-it'
import hljs from 'highlight.js'

// Configure markdown-it with syntax highlighting
const md = new MarkdownIt({
  html: false,        // Disable raw HTML for security
  linkify: true,      // Auto-convert URLs to links
  typographer: true,  // Enable smart quotes and other typography
  highlight: function (str, lang) {
    // Syntax highlighting for code blocks
    if (lang && hljs.getLanguage(lang)) {
      try {
        return `<pre class="hljs"><code>${hljs.highlight(str, { language: lang, ignoreIllegals: true }).value}</code></pre>`
      } catch (e) {
        console.error('Highlight.js error:', e)
      }
    }
    // Fallback: auto-detect language or just escape
    try {
      return `<pre class="hljs"><code>${hljs.highlightAuto(str).value}</code></pre>`
    } catch (e) {
      return `<pre class="hljs"><code>${md.utils.escapeHtml(str)}</code></pre>`
    }
  }
})

/**
 * Render markdown content to HTML
 * @param {string} content - Markdown content to render
 * @returns {string} Rendered HTML
 */
export function renderMarkdown(content) {
  if (!content) return ''
  return md.render(content)
}

export default md