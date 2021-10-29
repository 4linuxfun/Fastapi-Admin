<template lang="">
    <div>
        登录成功,token为{{token}}
    </div>
</template>
<script>

import {getToken} from '@/utils/auth'
export default {
    data(){
        return {
            token:getToken(),
        }
    }
    
}
</script>
<style lang="">
    
</style>