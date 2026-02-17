const flash = Process.findModuleByName("flash.ocx");
const base = flash.base;
const target = base.add(0x790d98);


let hook = null;

function startCatching() {
    stopCatching();
    hook = Interceptor.attach(target, {
        onEnter(args) {
            const candidate = args[0];

            try {
                // Быстрая проверка на символ '<' и '@'
                const firstS = candidate.readU16();
                if (firstS !== 0x3C && firstS !== 0x40) return;
                send(candidate.readUtf16String());
            } catch (e) {}
        }
    });
}


function stopCatching() {
    if (hook !== null) hook.detach();
    hook = null;
}




rpc.exports = {
    // Имя для вызова из Python : сама функция
    startcatching: startCatching,
    stopcatching: stopCatching
};