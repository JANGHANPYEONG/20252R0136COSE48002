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
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: CustomAppBar(
        title: context.read<DataAddHomeViewModel>().meatModel.id!,
        backButton: true,
        closeButton: false,
      ),
      body: SingleChildScrollView(
        child: Container(
          margin: EdgeInsets.symmetric(horizontal: 50.w),
          child: Column(
            children: [
              SizedBox(
                height: 25.h,
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '원육',
                    style: Palette.h3,
                  ),
                  Text(
                    context.read<DataAddHomeViewModel>().userId,
                    style: Palette.h5,
                  ),
                ],
              ),
              SizedBox(
                height: 15.w,
              ),
              SizedBox(
                height: 133.h,
                // 원육에 대한 추가데이터.
                child: OutlinedButton(
                  onPressed: () => context
                      .read<DataAddHomeViewModel>()
                      .clickedRawMeat(context),
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
                              Text(
                                  context
                                      .read<DataAddHomeViewModel>()
                                      .butcheryDate,
                                  style: Palette.h5Grey),
                              SizedBox(
                                height: 15.h,
                              ),
                              Text(
                                "${context.read<DataAddHomeViewModel>().species} > ${context.read<DataAddHomeViewModel>().secondary}",
                                style: TextStyle(
                                    fontSize: 36.sp,
                                    fontWeight: FontWeight.w700,
                                    color: Colors.black),
                              ),
                            ],
                          ),
                        ),
                        VerticalDivider(
                          thickness: 1,
                          color: Colors.grey[300],
                        ),
                        SizedBox(
                          width: 150.w,
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('추가정보 입력', style: Palette.h5LightGrey),
                              SizedBox(
                                height: 15.h,
                              ),
                              // 원육 데이터의 모든 데이터 입력 확인.
                              Text(
                                context
                                        .read<DataAddHomeViewModel>()
                                        .meatModel
                                        .rawmeatDataComplete!
                                    ? '완료'
                                    : '미완료',
                                style: TextStyle(
                                  fontSize: 28.sp,
                                  fontWeight: FontWeight.w700,
                                  color: context
                                          .read<DataAddHomeViewModel>()
                                          .meatModel
                                          .rawmeatDataComplete!
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
              SizedBox(
                height: 20.h,
              ),
              const Divider(
                height: 0,
                thickness: 10,
                color: Color.fromARGB(255, 250, 250, 250),
              ),
              SizedBox(
                height: 20.h,
              ),
              Row(
                children: [
                  Text('처리육', style: Palette.h3),
                ],
              ),
              SizedBox(
                height: 15.h,
              ),
              Row(
                children: [
                  Text('딥에이징 데이터', style: Palette.h4),
                  const Spacer(),
                ],
              ),
              SizedBox(
                height: 20.h,
              ),
              SizedBox(
                height: 450.h,
                // 딥에이징 추가 데이터 입력 (DeepAgingCard 컴포넌트 사용) - 클릭 | 삭제 시 대응되는 함수 호출
                child: context.watch<DataAddHomeViewModel>().isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : ListView.builder(
                        itemCount: context
                            .read<DataAddHomeViewModel>()
                            .meatModel
                            .deepAgingData!
                            .length,
                        itemBuilder: (BuildContext context, int index) {
                          return DeepAgingCard(
                            deepAgingNum: context
                                .read<DataAddHomeViewModel>()
                                .meatModel
                                .deepAgingData![index]["deepAgingNum"],
                            minute: context
                                .read<DataAddHomeViewModel>()
                                .meatModel
                                .deepAgingData![index]["minute"],
                            butcheryDate: context
                                .read<DataAddHomeViewModel>()
                                .meatModel
                                .deepAgingData![index]["date"],
                            completed: context
                                .read<DataAddHomeViewModel>()
                                .meatModel
                                .deepAgingData![index]["complete"],
                            isLast: index ==
                                    context
                                            .read<DataAddHomeViewModel>()
                                            .meatModel
                                            .deepAgingData!
                                            .length -
                                        1
                                ? true
                                : false,
                            onTap: () async => context
                                .read<DataAddHomeViewModel>()
                                .clickedProcessedMeat(index, context),
                            delete: () async => context
                                .read<DataAddHomeViewModel>()
                                .deleteList(index + 1),
                          );
                        },
                      ),
              ),
              SizedBox(
                height: 50.h,
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  SizedBox(
                    height: 133.h,
                    width: 588.w,
                    child: InkWell(
                      // 딥에이징 추가 데이터 추가
                      onTap: () => context
                          .read<DataAddHomeViewModel>()
                          .addDeepAgingData(context),
                      child: DottedBorder(
                        radius: Radius.circular(20.sp),
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
              SizedBox(
                height: 35.h,
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '총 처리 횟수 및 시간',
                    style: Palette.h4,
                  ),
                  Text(
                    context.watch<DataAddHomeViewModel>().total,
                    textAlign: TextAlign.center,
                    style: Palette.h3Green,
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
