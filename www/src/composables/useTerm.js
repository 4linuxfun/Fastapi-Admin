import {onMounted, ref, watch, onBeforeUnmount, nextTick} from 'vue'
import {FitAddon} from 'xterm-addon-fit'
import {Terminal} from 'xterm'
import 'xterm/css/xterm.css'

/**
 * @name: useTerm，用于统一使用terminal
 * @description: 终端
 * @return {Promise}
 *
 * 示例用法：
 * 创建终端
 * <div ref="terminalRef" style="width: 100%;height: 100%"/>
 * const terminalRef = ref(null)
 * const {term, initTerm} = useTerm(terminalRef)
 * 手动初始化
 * await initTerm()
 * 写入内容
 * term.value.write('写入terminal 内容\n')
 */
export default function useTerm(terminalRef) {
  const term = ref(null)
  const fitAddon = new FitAddon()

  async function initTerm() {
    if(!terminalRef.value){
      console.error('Terminal container not found')
      return
    }
    console.log('init terminal')
    term.value = new Terminal({
      rendererType: 'canvas',
      disableStdin: false,
      convertEol: true,
      cursorStyle: 'block',
      scrollback: 9999999,
    })
    term.value.open(terminalRef.value)
    term.value.loadAddon(fitAddon)

    await nextTick(async () => {
      fitAddon.fit()
      console.log('fit ok')
    })

    term.value.focus()
    console.log('init terminal ok')
  }

  const handleResize = () => {
    fitAddon.fit()
  }

  window.addEventListener('resize', handleResize)

  onBeforeUnmount(() => {
    window.removeEventListener('resize', handleResize)
  })

  return {
    term,
    initTerm
  }
}