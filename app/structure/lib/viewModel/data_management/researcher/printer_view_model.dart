import 'dart:async';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_blue_plus/flutter_blue_plus.dart';
import 'package:structure/model/meat_model.dart';

class PrinterViewModel extends ChangeNotifier {
  MeatModel meatModel;
  BuildContext context;

  PrinterViewModel(this.meatModel, this.context) {
    _initialize();
  }
  bool isLoading = true;
  bool isScanning = false;

  // Bluetooth
  List<BluetoothDevice> devices = [];
  BluetoothDevice? selectedDevice;
  bool isDeviceConnected = false;

  void _initialize() async {
    _flutterBlueSetting();
    await scan();

    isLoading = false;
    notifyListeners();
  }

  /// 블루투스 초기 값 설정
  void _flutterBlueSetting() async {
    // 블루투스를 지원하지 않음
    if (await FlutterBluePlus.isSupported == false) {
      debugPrint('Blueprint not supported');
      return;
    }

    FlutterBluePlus.adapterState.listen((BluetoothAdapterState state) {
      if (state == BluetoothAdapterState.on) {
        // 블루트스 활성화 상태
      } else if (state == BluetoothAdapterState.unauthorized) {
        // 블루트스 권한 없음 상태
      } else {
        // 기타 상태
      }
    });

    if (Platform.isAndroid) {
      await FlutterBluePlus.turnOn();
    }
  }

  /// 블루투스 기기 스캔
  Future<void> scan() async {
    isScanning = true;
    selectedDevice = null;
    isDeviceConnected = false;
    notifyListeners();

    // 리스트 초기화
    devices.clear();

    // 블루투스 기기 찾기
    await FlutterBluePlus.startScan(timeout: const Duration(seconds: 10));

    // 찾은 기기 저장
    var temp = FlutterBluePlus.onScanResults.listen(
      (results) async {
        if (results.isNotEmpty) {
          ScanResult r = results.last;
          if (r.advertisementData.advName.isNotEmpty) {
            devices.add(r.device);
            notifyListeners();
          }
        }
      },
    );

    // FlutterBluePrint에 저장된 기기 초기화
    FlutterBluePlus.cancelWhenScanComplete(temp);

    isScanning = false;
    notifyListeners();
  }

  /// 찾은 블루투스 기기 이름 반환하는 함수
  List<String> deviceNames() {
    return devices
        .map((device) => '${device.advName} : ${device.remoteId}')
        .toList();
  }

  /// 프린터 선택
  void selectPrinter(int index) async {
    isDeviceConnected = false;
    notifyListeners();

    if (selectedDevice != null) {
      // 이미 연결된 기기가 있으면 먼저 disconnect
      StreamSubscription subscription = selectedDevice!.connectionState
          .listen((BluetoothConnectionState state) async {
        if (state == BluetoothConnectionState.disconnected) {
          debugPrint(
              '${selectedDevice!.disconnectReason?.code} ${selectedDevice!.disconnectReason?.description}');
        }
      });
      selectedDevice!
          .cancelWhenDisconnected(subscription, delayed: true, next: true);
    }

    // 선택된 기기 설정
    selectedDevice = devices[index];
    await selectedDevice!.connect();
    isDeviceConnected = selectedDevice!.isConnected;

    notifyListeners();
  }

  /// 프린트 동작
  void printQR() async {
    // try {
    //   if (selectedDevice == null) {
    //     throw ErrorDescription('Printer not selected');
    //   }

    // } catch (e) {
    //   debugPrint('Error: $e');
    // }

    List<BluetoothService> services = await selectedDevice!.discoverServices();
    // for (var service in services) {
    //   if (service.uuid == Guid('00001101-0000-1000-8000-00805F9B34FB')) {
    //     for (var characteristic in service.characteristics) {
    //       if (characteristic.uuid ==
    //           Guid('00001101-0000-1000-8000-00805F9B34FB')) {
    //         List<int> bytes = utf8.encode("Hello, Printer!");
    //         await characteristic.write(bytes);
    //       } else {
    //         print('1');
    //       }
    //     }
    //   } else {
    //     print('2');
    //   }
    // }

    for (var service in services) {
      for (var characteristic in service.characteristics) {
        print(characteristic.uuid);
        // List<int> bytes = utf8.encode("Hello, Printer!");
        // await characteristic.write(bytes);
      }
    }

    // services.forEach((service) {
    //   print(service.uuid);
    //   if (service.uuid == Guid("YOUR_SERVICE_UUID")) {
    //     service.characteristics.forEach((characteristic) async {
    //       print(characteristic);
    //       if (characteristic.uuid == Guid("YOUR_CHARACTERISTIC_UUID")) {
    //         // 데이터 작성
    //         List<int> bytes = utf8.encode("Hello, Printer!");
    //         await characteristic.write(bytes);
    //       }
    //     });
    //   }
    // });
  }
}
