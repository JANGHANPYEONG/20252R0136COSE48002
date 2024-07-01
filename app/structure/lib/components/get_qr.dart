//
//
// QR Page 위젯.
// 데이터 관리 페이지에서, 관리 번호를 읽어올 때 이용한다.
//
//

import 'package:structure/config/pallete.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:go_router/go_router.dart';
import 'package:qr_code_scanner/qr_code_scanner.dart';

class GetQr extends StatefulWidget {
  const GetQr({
    super.key,
  });

  @override
  State<GetQr> createState() => _GetQrState();
}

class _GetQrState extends State<GetQr> {
  // Barcode 클래스는 code와 format으로 이루어진다.
  // format은 QR | barcode의 구분을 결정하며, code에는 정보가 담긴다.

  // result.code가 data에 저장된다.
  Barcode? result;
  String? data;
  // 카메라 작동 컨트롤러.
  QRViewController? controller;

  // Global Key
  final GlobalKey qrKey = GlobalKey(debugLabel: 'QR');

  @override
  void reassemble() {
    // 페이지가 작동할 때, 카메라를 초기화 한다.
    super.reassemble();
    controller!.pauseCamera();
    controller!.resumeCamera();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // 화면에 텍스트를 표현하기 위해 사용되었다.
          Column(
            children: <Widget>[
              Expanded(flex: 6, child: _buildQrView(context)),
            ],
          ),
          // 카메라 위에 내용을 올리기 위해 사용
          Positioned(
            top: 0,
            left: 0,
            right: 0,
            child: Container(
              padding: EdgeInsets.only(top: MediaQuery.of(context).padding.top),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Padding(
                    padding: EdgeInsets.only(left: 30.w),
                    child: Text(
                      'QR코드 스캔',
                      style: TextStyle(
                          fontSize: 34.sp,
                          fontWeight: FontWeight.w600,
                          color: Colors.white),
                    ),
                  ),
                  IconButton(
                    // QR 페이지에서 나간다.
                    icon: const Icon(Icons.close, color: Colors.white),
                    onPressed: () {
                      FocusScope.of(context).unfocus();
                      controller!.pauseCamera();
                      context.pop();
                    },
                  ),
                ],
              ),
            ),
          ),
          Positioned(
            // QR data가 들어가는 위치를 QR Bar 아래에 위치하기 위해 bottom Position을 조절한다.
            bottom: (MediaQuery.of(context).size.height -
                    MediaQuery.of(context).padding.top) *
                0.2,
            left: 0,
            right: 0,
            child: InkWell(
              // 데이터를 이전 페이지에 전달하고, 페이지를 widget tree에서 반환한다.
              onTap: (result != null)
                  ? () {
                      Navigator.pop(context, result!.code);
                    }
                  : null,
              child: Padding(
                padding: EdgeInsets.symmetric(horizontal: 50.w),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Container(
                      height: 90.h,
                      padding: EdgeInsets.all(5.w),
                      decoration: BoxDecoration(
                        color: Palette.confirmCardBg,
                        borderRadius: BorderRadius.circular(15.0),
                      ),
                      child: Container(
                        margin: const EdgeInsets.only(left: 10.0, right: 5.0),
                        child: Row(
                          children: [
                            Image.asset(
                              'assets/images/qr_scan.png',
                              height: 35.h,
                              width: 35.w,
                            ),
                            SizedBox(
                              width: 15.w,
                            ),
                            (result != null)
                                ? Text('${result!.code}')
                                : const Text(
                                    'QR코드를 스캔하세요.',
                                    style: TextStyle(
                                      color: Colors.white,
                                      fontSize: 15.0,
                                    ),
                                  ),
                            const Spacer(
                              flex: 1,
                            ),
                            const Icon(
                              Icons.arrow_forward_ios_outlined,
                              color: Colors.white,
                            )
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQrView(BuildContext context) {
    return QRView(
      // qr 화면 구성.
      key: qrKey,
      onQRViewCreated: _onQRViewCreated,
      overlay: QrScannerOverlayShape(
        // 이는 qr을 스캔하는 화면 overlay를 구성한다.
        borderColor: Colors.white,
        // 경계의 둥근 정도
        borderRadius: 15,
        // 경계가 채워질 정도의 길이 -> cutOutSize의 절반보다 작으면 경계가 없는 부분이 존재.
        borderLength: 140,
        // 두께
        borderWidth: 3,
        // 전반적인 layout 크기
        cutOutSize: 280,
      ),
    );
  }

  void _onQRViewCreated(QRViewController controller) {
    setState(() {
      this.controller = controller;
    });
    controller.scannedDataStream.listen((scanData) {
      // dataStream을 listen하여, provider의 기능을 이용한다.
      // 이곳에 오는 scanData는 Barcode 클래스이다.
      setState(() {
        result = scanData;
        data = result!.code;
      });
    });
  }

  @override
  void dispose() {
    controller?.dispose();
    super.dispose();
  }
}
