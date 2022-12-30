import {defineStore} from "pinia";
import {computed, ref} from 'vue'
import {GetDictItems} from '@/api/dictonary'

export const useDictStore = defineStore('dict', () => {
    const dictObject = ref({})
    // 通过dict，返回对应的值.构建一个带参数的getter
    const dictItems = computed(() => {
        return (dictName) => {
            if (!dictObject.value.hasOwnProperty(dictName)) {
                GetDictItems(dictName).then(response => {
                    dictObject.value[dictName] = response
                })
            }
            return dictObject.value[dictName]

        }
    })

    async function getDictItems(dictName) {
        if (!dictObject.value.hasOwnProperty(dictName)) {
            console.log('dictObject has no dict:'+dictName)
            dictObject.value[dictName] = await GetDictItems(dictName)
        }
        return dictObject.value[dictName]
    }

    return {dictObject, dictItems, getDictItems}
})