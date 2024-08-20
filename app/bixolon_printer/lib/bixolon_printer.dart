import 'bixolon_printer_platform_interface.dart';

class BixolonPrinter {
  Future<List<Object?>> findBluetoothPrinter() {
    return BixolonPrinterPlatform.instance.findBluetoothPrinter();
  }

  Future<bool> connectPrinter(String address) {
    return BixolonPrinterPlatform.instance.connectPrinter(address);
  }

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
  ) {
    return BixolonPrinterPlatform.instance.printQr(
      image,
      isTransparent,
      x,
      y,
      width,
      threshold,
      ditheringType,
      compressType,
      rotation,
    );
  }
}
