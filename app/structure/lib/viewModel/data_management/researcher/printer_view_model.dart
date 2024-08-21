import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:bixolon_printer/bixolon_printer.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:structure/components/custom_pop_up.dart';
import 'package:structure/model/meat_model.dart';
import 'package:http/http.dart' as http;
import 'package:go_router/go_router.dart';

class PrinterViewModel extends ChangeNotifier {
  MeatModel meatModel;
  BuildContext context;

  PrinterViewModel(this.meatModel, this.context) {
    _initialize();
  }
  bool isScanning = false;

  // Bluetooth
  BixolonPrinter bixolonPrinter = BixolonPrinter();
  List<String> devices = [];
  List<String> deviceNames = [];
  String? selectedDevice;
  bool isDeviceConnected = false;

  void _initialize() async {
    await scan();
  }

  /// 등록된 블루투스 기기 스캔
  Future<void> scan() async {
    isScanning = true;
    selectedDevice = null;
    notifyListeners();

    try {
      var pairedDevices = await bixolonPrinter.findBluetoothPrinter();
      devices = pairedDevices
          .cast<String>()
          .where((device) => device.startsWith('SPP')) //SPP로 시작하는 장치만 가져옴
          .toList();
      deviceNames =
          devices.map((device) => device.split('(')[0].trim()).toList();
    } catch (e) {}

    // 만약 프린터가 하나만 발견된다면 바로 연결까지 진행
    if (devices.length == 1) {
      selectPrinter(0);
    }

    isScanning = false;
    notifyListeners();
  }

  /// 프린터 선택
  void selectPrinter(int index) async {
    isScanning = false;
    isDeviceConnected = false;
    notifyListeners();

    showPrinterConnectPopup(context);

    // 프린터 선택
    selectedDevice = devices[index].split('(')[0].trim();
    // 프린터 주소 추출
    final address = devices[index].split('(')[1].replaceAll(')', '').trim();
    try {
      // 프린터 연결
      isDeviceConnected = await bixolonPrinter
          .connectPrinter(address)
          .timeout(const Duration(seconds: 4));

      if (context.mounted) context.pop();
    } catch (e) {
      if (context.mounted) {
        context.pop();
        showPrinterConnectErrorPopup(context);
      }
    }

    notifyListeners();
  }

  /// 프린트 동작
  void printQR() async {
    showPrintPopup(context);
    if (meatModel.imagePath != null) {
      String qrString = await loadQr();
      await bixolonPrinter.printQr(qrString, true, 60, 10, 450, 100, 80, 0, 0);
    }
    if (context.mounted) context.pop();
  }

  /// S3에 저장된 QR 이미지를 프린트 가능한 문자열로 변환하는 함수
  Future<String> loadQr() async {
    Uint8List imageBytes;

    if (meatModel.imagePath!.contains('http')) {
      final response = await http.get(Uri.parse(meatModel.imagePath!));
      if (response.statusCode == 200) {
        imageBytes = response.bodyBytes;
      } else {
        throw Exception('Failed to load image from S3 server');
      }
    } else {
      final file = File(meatModel.imagePath!);
      imageBytes = await file.readAsBytes();
    }

    String base64Image = base64Encode(imageBytes);
    return base64Image;
  }
}
