import {GET, POST, PUT, DELETE} from '@/utils/request'

export const GetSysApis = (q, direction, id, limit, offset_page) => GET('api/sysapis', {
  q,
  direction,
  id,
  limit,
  offset_page
})