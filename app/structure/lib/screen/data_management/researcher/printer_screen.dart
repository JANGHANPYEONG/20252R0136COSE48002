import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/custom_drop_down.dart';
import 'package:structure/components/image_card.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/viewModel/data_management/researcher/printer_view_model.dart';

class PrinterScreen extends StatefulWidget {
  const PrinterScreen({super.key});

  @override
  State<PrinterScreen> createState() => _PrinterScreenState();
}

class _PrinterScreenState extends State<PrinterScreen> {
  @override
  Widget build(BuildContext context) {
    PrinterViewModel printerViewModel = context.watch<PrinterViewModel>();

    return Scaffold(
      appBar: const CustomAppBar(title: 'QR 프린트'),
      body: Container(
        margin: EdgeInsets.symmetric(horizontal: 40.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(height: 24.h),

            // 프린터 리스트
            Row(
              children: [
                // 리스트 dropdown
                Expanded(
                  child: CustomDropdown(
                    hintText: Text('프린터를 선택하세요', style: Palette.h4OnSecondary),
                    value: printerViewModel.selectedDevice ??
                        (printerViewModel.devices.isEmpty
                            ? '프린터를 찾을 수 없습니다'
                            : '프린터를 선택하세요'),
                    itemList: printerViewModel.deviceNames,
                    onChanged: (_, index) =>
                        printerViewModel.selectPrinter(index),
                  ),
                ),

                // 새로고침 버튼
                IconButton(
                  onPressed: () async => await printerViewModel.scan(),
                  icon: printerViewModel.isScanning
                      ? SizedBox(
                          width: 32.w,
                          height: 32.w,
                          child: const LoadingScreen())
                      : const Icon(Icons.refresh),
                ),
              ],
            ),
            SizedBox(height: 32.h),

            // QR 미리보기
            Text('미리보기', style: Palette.h4),
            SizedBox(height: 16.h),

            ImageCard(imagePath: printerViewModel.meatModel.imagePath),
            const Spacer(),

            Container(
              margin: EdgeInsets.only(bottom: 40.h),
              child: MainButton(
                width: double.infinity,
                height: 96.h,
                text: printerViewModel.selectedDevice == null
                    ? '프린터 선택'
                    : printerViewModel.isDeviceConnected
                        ? '프린트'
                        : '프린터 연결',
                onPressed: printerViewModel.isDeviceConnected
                    ? () => printerViewModel.printQR()
                    : null,
              ),
            )
          ],
        ),
      ),
    );
  }
}
