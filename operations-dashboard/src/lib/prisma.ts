import { PrismaClient } from '../generated/prisma/client'
import { PrismaLibSql } from '@prisma/adapter-libsql'
import path from 'path'

const globalForPrisma = globalThis as unknown as {
  prisma: PrismaClient | undefined
}

const getDbUrl = () => {
  const url = process.env.DATABASE_URL || 'file:./prisma/dev.db'
  if (url.startsWith('file:')) {
    const relPath = url.replace('file:', '')
    return `file:${path.resolve(process.cwd(), relPath)}`
  }
  return url
}

const adapter = new PrismaLibSql({ url: getDbUrl() })

export const prisma = globalForPrisma.prisma ?? new PrismaClient({ adapter })

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma

export default prisma