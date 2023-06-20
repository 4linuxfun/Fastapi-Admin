import {GET, POST, PUT, DELETE} from '@/utils/request'

export const PostNewCronJob = (dict) => POST('/api/jobs/', dict)
export const GetJobList = () => GET('/api/jobs/')
export const DelJob = (jobId) => DELETE('/api/jobs/' + jobId)
export const PutCronJob = (job) => PUT('/api/jobs/', job)
export const SwitchJob = (jobId) => GET('/api/jobs/switch/' + jobId)
export const GetLogs = (jobId) => GET('/api/jobs/logs')