import {GET, POST, PUT, DELETE} from '@/utils/request'

// 用户相关接口
export const PostNewGroup = (group) => POST('/api/host/group', group)
export const GetAllGroup = () => GET('/api/host/group')
export const DelGroup = (groupId) => DELETE('/api/host/group/' + groupId)
export const PostNewHost = (host) => POST('/api/host', host)
export const PutHost = (host) => PUT('/api/host', host)
export const DelHost = (hostId) => DELETE('/api/host/' + hostId)
export const PingHost = (hostId) => GET('/api/host/ping/' + hostId)
export const GetHostById = (hostId) => GET('/api/host/' + hostId)