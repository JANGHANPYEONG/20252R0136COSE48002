//
//
// 데이터 관리 페이지(View) : Normal
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/custom_table_bar.dart';
import 'package:structure/components/filter_box.dart';
import 'package:structure/components/list_card_normal.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_text_field.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/config/userfuls.dart';
import 'package:structure/viewModel/data_management/normal/data_management_view_model.dart';

class DataManagementNormalScreen extends StatefulWidget {
  const DataManagementNormalScreen({super.key});

  @override
  State<DataManagementNormalScreen> createState() =>
      _DataManagementNormalScreenState();
}

class _DataManagementNormalScreenState
    extends State<DataManagementNormalScreen> {
  @override
  Widget build(BuildContext context) {
    DataManagementHomeViewModel dataManagementHomeViewModel =
        context.watch<DataManagementHomeViewModel>();

    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        appBar: const CustomAppBar(
          title: '데이터 관리',
          backButton: true,
          closeButton: false,
        ),
        body: Stack(
          children: [
            SingleChildScrollView(
              scrollDirection: Axis.vertical,
              // 드래그시 키보드 닫기
              keyboardDismissBehavior: ScrollViewKeyboardDismissBehavior.onDrag,
              child: Container(
                margin: EdgeInsets.symmetric(horizontal: 40.w),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    SizedBox(height: 24.h),

                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        // 데이터 개수 텍스트
                        SizedBox(
                          child: Text(
                            '${dataManagementHomeViewModel.selectedList.length}개의 데이터',
                            textAlign: TextAlign.left,
                            style: Palette.h5Secondary,
                          ),
                        ),

                        // 필터 버튼
                        InkWell(
                          // 필터 버튼을 누르면 'clickedFilter'함수를 참조한다.
                          onTap: () =>
                              dataManagementHomeViewModel.clickedFilter(),
                          child: Container(
                            padding: EdgeInsets.all(16.w),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(
                                  dataManagementHomeViewModel.filterdResult,
                                  style: Palette.h4,
                                ),
                                dataManagementHomeViewModel.isOpnedFilter
                                    ? const Icon(Icons.arrow_drop_up_outlined)
                                    : const Icon(Icons.arrow_drop_down),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),

                    // 'isOpendFilter'변수를 참조하여 filter를 표출한다.
                    dataManagementHomeViewModel.isOpnedFilter
                        ? FilterBox(
                            type: 0,
                            dateList: dataManagementHomeViewModel.dateList,
                            onTapDate: (index) =>
                                dataManagementHomeViewModel.onTapDate(index),
                            dateStatus: dataManagementHomeViewModel.dateStatus,
                            firstDayText:
                                dataManagementHomeViewModel.firstDayText,
                            indexDay: dataManagementHomeViewModel.indexDay,
                            firstDayOnTapTable: () =>
                                dataManagementHomeViewModel.onTapTable(0),
                            lastDayText:
                                dataManagementHomeViewModel.lastDayText,
                            lastDayOnTapTable: () =>
                                dataManagementHomeViewModel.onTapTable(1),
                            isOpenTable:
                                dataManagementHomeViewModel.isOpenTable,
                            focused: dataManagementHomeViewModel.focused,
                            onDaySelected: (selectedDay, focusedDay) =>
                                dataManagementHomeViewModel.onDaySelected(
                                    selectedDay, focusedDay),
                            checkedFilter:
                                dataManagementHomeViewModel.checkedFilter(),
                            onPressedFilterSave: () =>
                                dataManagementHomeViewModel
                                    .onPressedFilterSave(),
                            statusList: dataManagementHomeViewModel.statusList,
                            onTapstatus: (index) =>
                                dataManagementHomeViewModel.onTapStatus(index),
                            statusStatus:
                                dataManagementHomeViewModel.statusStatus,
                            sortList: dataManagementHomeViewModel.sortList,
                            onTapSort: (index) =>
                                dataManagementHomeViewModel.onTapSort(index),
                            sortStatus: dataManagementHomeViewModel.sortStatus)
                        : SizedBox(height: 16.h),

                    //
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        // 'MainTextField' 컴포넌트를 이용하여 관리 번호 검색 기능을 정의한다.
                        Expanded(
                          child: MainTextField(
                            width: double.infinity,
                            height: 80.h,
                            mainText: '관리번호 입력',
                            validateFunc: null,
                            onSaveFunc: null,
                            controller: dataManagementHomeViewModel.controller,
                            onChangeFunc: (value) =>
                                dataManagementHomeViewModel.onChanged(value),
                            focusNode: dataManagementHomeViewModel.focusNode,
                            canAlert: false,
                            prefixIcon: const Icon(Icons.search),
                            suffixIcon:
                                dataManagementHomeViewModel.focusNode.hasFocus
                                    ? IconButton(
                                        onPressed: () {
                                          dataManagementHomeViewModel
                                              .textClear(context);
                                        },
                                        icon: const Icon(
                                          Icons.cancel_outlined,
                                          color: Colors.black,
                                        ),
                                      )
                                    : null,
                          ),
                        ),
                        SizedBox(width: 16.w),

                        IconButton(
                          // QR 코드 확인 기능을 정의한다.
                          iconSize: 48.w,
                          onPressed: () async =>
                              dataManagementHomeViewModel.clickedQr(context),
                          icon: const Icon(Icons.qr_code_scanner_rounded),
                        ),
                      ],
                    ),
                    SizedBox(height: 16.h),

                    // TODO : 통일
                    const CustomTableNormalBar(isNormal: true),
                    SizedBox(height: 16.h),

                    SizedBox(
                      height: 800.h,
                      child: Scrollbar(
                        thumbVisibility: true,
                        child: ListView.builder(
                          itemCount:
                              dataManagementHomeViewModel.selectedList.length,
                          itemBuilder: (context, index) => ListCardNormal(
                            onTap: () async => await dataManagementHomeViewModel
                                .onTap(index, context),
                            num: dataManagementHomeViewModel.selectedList[index]
                                ["meatId"]!,
                            dayTime: dataManagementHomeViewModel
                                .selectedList[index]["createdAt"]!,
                            statusType: dataManagementHomeViewModel
                                .selectedList[index]["statusType"]!,
                            dDay: 3 -
                                Usefuls.calculateDateDifference(
                                  Usefuls.dateShortToDateLong(
                                      dataManagementHomeViewModel
                                          .selectedList[index]["createdAt"]!),
                                ),
                          ),
                        ),
                      ),
                    ),
                    SizedBox(height: 40.h),
                  ],
                ),
              ),
            ),
            dataManagementHomeViewModel.isLoading
                ? const Center(child: LoadingScreen())
                : Container(),
          ],
        ),
      ),
    );
  }
}
