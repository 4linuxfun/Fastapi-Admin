import {GET, POST, PUT, DELETE} from '@/utils/request'

//playbook相关接口
export const GetPlaybook = (playbookId) => GET('/api/playbook/' + playbookId)
export const PostNewPlaybook = (playbook) => POST('/api/playbook', playbook)
export const PutPlaybook = (playbook) => PUT('/api/playbook', playbook)
export const DelPlaybook = (playbookId) => DELETE('/api/playbook/' + playbookId)
export const GetPlaybooksByQuery = (query) => GET('/api/playbook', {query})