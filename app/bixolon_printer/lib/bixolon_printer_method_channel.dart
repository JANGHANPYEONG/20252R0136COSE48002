import 'package:flutter/foundation.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';

import 'bixolon_printer_platform_interface.dart';

/// An implementation of [BixolonPrinterPlatform] that uses method channels.
class MethodChannelBixolonPrinter extends BixolonPrinterPlatform {
  /// The method channel used to interact with the native platform.
  @visibleForTesting
  final methodChannel = const MethodChannel('bixolon_printer');

  @override
  Future<List<Object?>> findBluetoothPrinter() async {
    try {
      final result = await methodChannel.invokeMethod('findBluetoothPrinter');
      return result;
    } catch (e) {
      throw Exception('Error finding bluetooth printer: $e');
    }
  }

  @override
  Future<bool> connectPrinter(String address) async {
    try {
      final result = await methodChannel
          .invokeMethod('connectPrinter', {'address': address});
      return result;
    } catch (e) {
      throw Exception('Error connecting to bluetooth printer: $e');
    }
  }

  @override
  Future<bool> printQr(
    String image,
    bool isTransparent,
    int x,
    int y,
    int width,
    int threshold,
    int ditheringType,
    int compressType,
    int rotation,
  ) async {
    try {
      final result = await methodChannel.invokeMethod('printQr', {
        'image': image,
        'isTransparent': isTransparent,
        'x': x,
        'y': y,
        'width': width,
        'threshold': threshold,
        'ditheringType': ditheringType,
        'compressType': compressType,
        'rotation': rotation,
      });
      return result;
    } catch (e) {
      throw Exception('Error printing QR: $e');
    }
  }
}
