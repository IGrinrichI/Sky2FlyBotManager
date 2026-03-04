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




let isAutoLooterActive = true;
let sendInterval = 1000;

function pauseAutoLooter() {
    isAutoLooterActive = false;
}

function resumeAutoLooter() {
    isAutoLooterActive = true;
}

function setSendInterval(ms) {
    sendInterval = ms;
}


function areUint8ArraysEqual(arr1, arr2) {
  if (arr1.length !== arr2.length) return false;
  for (let i = 0; i < arr1.length; i++) {
    if (arr1[i] !== arr2[i]) return false;
  }
  return true;
}

function getPackets(packet) {
    const packetLength = packet.length;
    const packets = [];
    if (packetLength < 3) return packets;

    let index = 0;

    while (index < packetLength) {
        try {
            const packetP = packet.slice(index);
            const headerLen = 2;
            const header = packetP.slice(0, headerLen);
            let dataLen = 0;
            let addLen = 2;

            if (areUint8ArraysEqual(header, [0x80, 0x00]) || areUint8ArraysEqual(header, [0x90, 0x00])) {
                packets.push(header);
                index += headerLen;
                continue;
            }

            if (areUint8ArraysEqual(header, [0x91, 0x20])) {
                dataLen = 2;
                addLen = 0;
            } else {
                if (header[1] >> 4 === 0x1){
                    dataLen = packetP[headerLen] | (packetP[headerLen + 1] << 8);
                } else {
                    dataLen = packetP[headerLen];
                }
            }

            if (areUint8ArraysEqual(header, [0x69, 0x80])) {
                addLen = 1;
            }

            let packetPLength = headerLen + dataLen + addLen;
            packets.push(packetP.slice(0, packetPLength));
            index = index + packetPLength;
        } catch (e) {
            console.log("Ошибка при разборе пакета.", packet);
            return packets;
        };
    }

    return packets;
}


function autoLooter() {
    const recvPtr = Process.findModuleByName("ws2_32.dll").findExportByName("recv");
    const sendPtr = Process.findModuleByName("ws2_32.dll").findExportByName("send");
    const sendFunc = new NativeFunction(sendPtr, 'int', ['pointer', 'pointer', 'int', 'int']);

    const toKey = (arr) => arr.join(',');
    let objectTraker = new Map(); // ID объекта (2 байта) -> ID лута, тип лута, короче это 6 байтов
    let lootTraker = new Map(); // ID лута, тип лута, короче это 6 байтов -> ID объекта (2 байта)
    let currentItemIdArray = [];

    Interceptor.attach(recvPtr, {
        onEnter(args) {
            this.buf = args[1];
            this.fd = args[0];
        },
        onLeave(retval) {
            const len = retval.toInt32();
            if (len <= 0) return;
            let fd = this.fd;
            const data = new Uint8Array(this.buf.readByteArray(len));

            let alreadyPickedUpStartIndex = -1;
            let itemsToPickUp = [];

            getPackets(data).forEach((data, packetIndex) => {
                // 1. ЛОВИМ ПОЯВЛЕНИЕ (Spawn)
                try {
                    const packetHeader = data.slice(0, 2);
                    if (areUint8ArraysEqual(packetHeader, [0x05, 0x11])) { // Ответ на подбор лута
                        if (alreadyPickedUpStartIndex === -1) alreadyPickedUpStartIndex = packetIndex;
                        if (areUint8ArraysEqual(data.slice(4, 4 + 2), [0x0c, 0x02])) {
                            let indexToRemove = packetIndex - alreadyPickedUpStartIndex;
                            try {
                                let itemId = currentItemIdArray[indexToRemove];
                                let lidKey = toKey(itemId);
                                let oidKey = toKey(lootTraker.get(lidKey));
                                lootTraker.delete(lidKey);
                                objectTraker.delete(oidKey);
                            } catch (e) { }
                        }
                    } else if (areUint8ArraysEqual(packetHeader, [0x09, 0x11])) { // Появление лута на радаре
                        if (!lootTraker.has(toKey(data.slice(7, 7 + 6)))) {
                            objectTraker.set(toKey(data.slice(13, 13 + 2)), data.slice(7, 7 + 6));
                            lootTraker.set(toKey(data.slice(7, 7 + 6)), data.slice(13, 13 + 2));
                            itemsToPickUp.push(data.slice(7, 7 + 6));
                        }
                    } else if (areUint8ArraysEqual(packetHeader, [0xd3, 0x10])) { // Выпадение пушинки с одуванчика
                        objectTraker.set(toKey(data.slice(13, 13 + 2)), data.slice(7, 7 + 6));
                        lootTraker.set(toKey(data.slice(7, 7 + 6)), data.slice(13, 13 + 2));
                        itemsToPickUp.push(data.slice(7, 7 + 6));
                    } else if (areUint8ArraysEqual(packetHeader, [0xd5, 0x10])) { // Подобран лут
                        try {
                            let oid = data.slice(5, 5 + 2);
                            let oidKey = toKey(oid);
                            let lidKey = toKey(objectTraker.get(oidKey));
                            objectTraker.delete(oidKey);
                            lootTraker.delete(lidKey);
                        } catch (e) { }
                    } else if (areUint8ArraysEqual(packetHeader, [0x75, 0x10])) { // Подобран лут (контейнер/босс?)
                        try {
                            let oid = data.slice(5, 5 + 2);
                            let oidKey = toKey(oid);
                            let lidKey = toKey(objectTraker.get(oidKey));
                            objectTraker.delete(oidKey);
                            lootTraker.delete(lidKey);
                        } catch (e) { }
                    } else if (areUint8ArraysEqual(packetHeader, [0xd8, 0x10])) { // Всплытие лута из под неба
                        objectTraker.set(toKey(data.slice(13, 13 + 2)), data.slice(7, 7 + 6));
                        lootTraker.set(toKey(data.slice(7, 7 + 6)), data.slice(13, 13 + 2));
                        itemsToPickUp.push(data.slice(7, 7 + 6));
                    } else if (areUint8ArraysEqual(packetHeader, [0x68, 0x10])) { // Появление моба на радаре
                        objectTraker.set(toKey(data.slice(13, 13 + 2)), data.slice(7, 7 + 6));
                        lootTraker.set(toKey(data.slice(7, 7 + 6)), data.slice(13, 13 + 2));
                        // Запуск подбора надо делать только для особого формата пакета,
                        // как смерть медузы или появление трупа на горизонте
                        let currentHP = data[28] | (data[29] << 8) | (data[30] << 16) | (data[31] << 24);
                        if (currentHP === 0) itemsToPickUp.push(data.slice(7, 7 + 6));
                    } else if (areUint8ArraysEqual(packetHeader, [0x30, 0x11])) { // Смерть моба ?
                        if (data.length < 10) return;
                        itemsToPickUp.push(objectTraker.get(toKey(data.slice(10, 10 + 2))));
                    } else if (areUint8ArraysEqual(packetHeader, [0x16, 0x11])) { // Разрыв
                        itemsToPickUp.push(data.slice(7, 7 + 6));
                        objectTraker.set(toKey(data.slice(13, 13 + 2)), data.slice(7, 7 + 6));
                        lootTraker.set(toKey(data.slice(7, 7 + 6)), data.slice(13, 13 + 2));
                    } /*else if (areUint8ArraysEqual(packetHeader, [0x66, 0x10])) { // Мертвый моб ? ушел под небо (поднебки)
                        if (data[4] !== 0x18) return;
                        console.log(`Обнаружен моб под небом ${toKey(data.slice(5, 5 + 2))} с id предмета ${toKey(objectTraker.get(toKey(data.slice(5, 5 + 2))))}`);
//                        itemsToPickUp.push(objectTraker.get(toKey(data.slice(5, 5 + 2))));
                    }*/
                } catch (e) {}
            });

            if (itemsToPickUp.length !== 0) autoPickupArray(fd, itemsToPickUp, true);
        }
    });


    function autoPickupArray(socketHandle, itemIdArray, firstTime) {
        if (itemIdArray.length == 0 || !socketHandle) return;

        let packetsToSend = [];

        itemIdArray.forEach((itemId) => {
            if (!firstTime && !lootTraker.has(toKey(itemId))) return;
            packetsToSend.push(itemId);
        });

        if (packetsToSend.length === 0) return;

        currentItemIdArray = packetsToSend;
        const packetLength = 24 * packetsToSend.length;
        const packets = Memory.alloc(packetLength);

        packetsToSend.forEach((itemId, packetIndex) => {
            const packetOffset = packetIndex * 24;
            packets.add(packetOffset).writeByteArray([0x06, 0x11, 0x08, 0x00, 0x03, 0x00]);
            packets.add(packetOffset + 6).writeByteArray(itemId);
            packets.add(packetOffset + 12).writeByteArray([0x19, 0x11, 0x08, 0x00, 0x03, 0x00]);
            packets.add(packetOffset + 18).writeByteArray(itemId);
        });

        if (isAutoLooterActive) sendFunc(socketHandle, packets, packetLength, 0);

        setTimeout(() => { autoPickupArray(socketHandle, packetsToSend); }, sendInterval);
    }
}




rpc.exports = {
    // Имя для вызова из Python : сама функция
    startcatching: startCatching,
    stopcatching: stopCatching,
    autolooter: autoLooter,
    resumeautolooter: resumeAutoLooter,
    pauseautolooter: pauseAutoLooter,
    setsendinterval: setSendInterval
};