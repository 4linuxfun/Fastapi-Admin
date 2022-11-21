import {GET, POST, PUT, DELETE} from '@/utils/request'

export const PostNewDict = (dict) => POST('/api/dict', dict)
export const PutDict = (dict) => PUT('/api/dict', dict)
export const PostNewDictItem = (item) => POST('/api/dict/item', item)
export const PutDictItem = (item) => PUT('/api/dict/item', item)
export const DelDictItem = (id) => DELETE('/api/dict/item/' + id)
export const GetDictItems = (code) => GET('/api/dict/'+ code)
