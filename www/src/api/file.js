import request from '@/utils/request'

export function downloadFile(url,method,data=null){
	let config = {
				url:url,
				method:method,
				responseType:"blob"
			}
	if(method === "post"){
		config['data']=	data
	}
	request(config).then((res)=>{
						let url = window.URL.createObjectURL(new Blob([res.data]))
						let a = document.createElement('a')
						a.style.display = 'none'
						a.href = url
						a.setAttribute('download',res.filename)
						document.body.appendChild(a)
						a.click()
						document.body.removeChild(a)
					})
}