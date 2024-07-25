//
//
// 데이터 추가 페이지(View) : Researcher
//
//

import 'package:dotted_border/dotted_border.dart';
import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/deep_aging_card.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/data_management/researcher/data_add_home_view_model.dart';

class DataAddHome extends StatefulWidget {
  const DataAddHome({super.key});

  @override
  State<DataAddHome> createState() => _DataAddHomeState();
}

class _DataAddHomeState extends State<DataAddHome> {
  @override
  Widget build(BuildContext context) {
    DataAddHomeViewModel dataAddHomeViewModel =
        context.watch<DataAddHomeViewModel>();

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: CustomAppBar(
        title: dataAddHomeViewModel.meatModel.meatId!,
        backButton: true,
        closeButton: false,
      ),
      body: SingleChildScrollView(
        child: Container(
          margin: EdgeInsets.symmetric(horizontal: 50.w),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SizedBox(height: 25.h),
              // 원육
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('원육', style: Palette.h3),
                  Text(
                    dataAddHomeViewModel.userName,
                    style: Palette.h5,
                  ),
                ],
              ),
              SizedBox(height: 15.h),

              // 원육 추가데이터
              SizedBox(
                height: 133.h,
                // 원육에 대한 추가데이터.
                child: OutlinedButton(
                  onPressed: () => dataAddHomeViewModel.clickedRawMeat(context),
                  style: OutlinedButton.styleFrom(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(15.r),
                    ),
                    side: const BorderSide(color: Color(0xFFEAEAEA)),
                  ),
                  child: Padding(
                    padding: EdgeInsets.symmetric(vertical: 15.h),
                    child: Row(
                      children: [
                        SizedBox(
                          width: 350.w,
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              // 도축 날짜
                              Text(
                                dataAddHomeViewModel.butcheryDate,
                                style: Palette.h5Grey,
                              ),
                              SizedBox(height: 15.h),

                              // 종 > 부위
                              Text(
                                '${dataAddHomeViewModel.speciesValue} > ${dataAddHomeViewModel.secondary}',
                                style: TextStyle(
                                  fontSize: 36.sp,
                                  fontWeight: FontWeight.w700,
                                  color: Colors.black,
                                ),
                              ),
                            ],
                          ),
                        ),
                        VerticalDivider(thickness: 1, color: Colors.grey[300]),

                        // 추가정보 입력
                        SizedBox(
                          width: 150.w,
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('추가정보 입력', style: Palette.h5LightGrey),
                              SizedBox(height: 15.h),

                              // 원육 데이터의 모든 데이터 입력 확인.
                              Text(
                                dataAddHomeViewModel.meatModel.rawCompleted
                                    ? '완료'
                                    : '미완료',
                                style: TextStyle(
                                  fontSize: 28.sp,
                                  fontWeight: FontWeight.w700,
                                  color: dataAddHomeViewModel
                                          .meatModel.rawCompleted
                                      ? const Color.fromARGB(255, 56, 197, 95)
                                      : const Color.fromARGB(255, 255, 73, 73),
                                ),
                              ),
                            ],
                          ),
                        )
                      ],
                    ),
                  ),
                ),
              ),
              SizedBox(height: 40.h),

              const Divider(
                height: 0,
                thickness: 10,
                color: Color.fromARGB(255, 250, 250, 250),
              ),
              SizedBox(height: 20.h),

              // 처리육, 딥에이징 데이터 텍스트
              Text('처리육', style: Palette.h3),
              SizedBox(height: 15.h),
              Text('딥에이징 데이터', style: Palette.h4),
              SizedBox(height: 20.h),

              // 딥에이징 리스트
              SizedBox(
                height: 450.h,
                // 딥에이징 추가 데이터 입력 (DeepAgingCard 컴포넌트 사용) - 클릭 | 삭제 시 대응되는 함수 호출
                // index 0은 원육 정보이기 때문에 index + 1 부터 리스트에 표시해야 함
                child: dataAddHomeViewModel.isLoading
                    ? const Center(child: LoadingScreen())
                    : ListView.builder(
                        itemCount: dataAddHomeViewModel
                                .meatModel.deepAgingInfo!.length -
                            1,
                        itemBuilder: (BuildContext context, int index) {
                          return Padding(
                            padding: const EdgeInsets.symmetric(vertical: 4.0),
                            child: DeepAgingCard(
                              deepAgingNum:
                                  '${dataAddHomeViewModel.meatModel.deepAgingInfo![index + 1]['seqno']}회',
                              minute: dataAddHomeViewModel.meatModel
                                  .deepAgingInfo![index + 1]['minute'],
                              butcheryDate: dataAddHomeViewModel
                                  .meatModel.deepAgingInfo![index + 1]['date'],
                              // TODO : complete check
                              completed: false,
                              // dataAddHomeViewModel
                              //     .meatModel.deepAgingInfo![index]['complete'],
                              onTap: () async => dataAddHomeViewModel
                                  .clickedProcessedMeat(index + 1, context),
                              delete: () async =>
                                  dataAddHomeViewModel.deleteList(index + 1),
                            ),
                          );
                        },
                      ),
              ),
              SizedBox(height: 50.h),

              // 딥에이징 데이터 추가 버튼
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  SizedBox(
                    height: 133.h,
                    width: 588.w,
                    child: InkWell(
                      onTap: () =>
                          dataAddHomeViewModel.addDeepAgingData(context),
                      child: DottedBorder(
                        radius: Radius.circular(20.r),
                        borderType: BorderType.RRect,
                        color: Palette.notEditableBg,
                        strokeWidth: 2.sp,
                        dashPattern: [10.w, 10.w],
                        child: SizedBox(
                          width: 640.w,
                          height: 653.h,
                          child: Image.asset(
                            'assets/images/add_circle.png',
                            cacheWidth: 45,
                            cacheHeight: 45,
                          ),
                        ),
                      ),
                    ),
                  ),
                ],
              ),
              SizedBox(height: 30.h),
              const Divider(
                height: 0,
                thickness: 0.8,
                color: Color(0xFFEAEAEA),
              ),
              SizedBox(height: 5.h),
              Column(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '총 처리 횟수 및 시간',
                        style: Palette.h4,
                      ),
                      Text(
                        dataAddHomeViewModel.total,
                        textAlign: TextAlign.center,
                        style: Palette.h3Green,
                      ),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
