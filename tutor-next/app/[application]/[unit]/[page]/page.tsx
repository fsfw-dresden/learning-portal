import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

export async function generateStaticParams() {
  const markdownDir = path.join(process.cwd(), 'markdown')
  const applications = fs.readdirSync(markdownDir)
  
  const paths: { application: string, unit: string, page: string }[] = []
  
  applications.forEach(application => {
    const unitsDir = path.join(markdownDir, application)
    const units = fs.readdirSync(unitsDir)
    
    units.forEach(unit => {
      const pagesDir = path.join(unitsDir, unit)
      const pages = fs.readdirSync(pagesDir)
      
      pages.forEach(page => {
        paths.push({
          application,
          unit,
          page: page.replace('.md', '')
        })
      })
    })
  })
  
  return paths
}

export default function Page({ params }: { params: { application: string, unit: string, page: string } }) {
  const { application, unit, page } = params
  const markdownPath = path.join('markdown', application, unit, `${page}.md`)
  const fileContents = fs.readFileSync(markdownPath, 'utf8')
  const { data, content } = matter(fileContents)
  const htmlContent = md.render(content)

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">{data.title}</h1>
      <div dangerouslySetInnerHTML={{ __html: htmlContent }} />
    </div>
  )
}
