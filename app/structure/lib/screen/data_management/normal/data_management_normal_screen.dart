//
//
// 데이터 관리 페이지(View) : Normal
//
//

import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/custom_divider.dart';
import 'package:structure/components/custom_table_bar.dart';
import 'package:structure/components/filter_box.dart';
import 'package:structure/components/list_card.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_text_field.dart';
import 'package:structure/config/palette.dart';
import 'package:structure/config/usefuls.dart';
import 'package:structure/viewModel/data_management/normal/data_management_normal_view_model.dart';

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
    DataManagementNormalViewModel dataManagementNormalViewModel =
        context.watch<DataManagementNormalViewModel>();

    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        appBar: const CustomAppBar(title: '데이터 관리'),
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
                          '${dataManagementNormalViewModel.selectedList.length}개의 데이터',
                          textAlign: TextAlign.left,
                          style: Palette.h5Secondary,
                        )),

                        // 필터 버튼
                        InkWell(
                          onTap: () =>
                              dataManagementNormalViewModel.clickedFilter(),
                          borderRadius: BorderRadius.circular(20.r),
                          child: Container(
                            padding: EdgeInsets.all(16.w),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(
                                  dataManagementNormalViewModel.filterdResult,
                                  style: Palette.h4,
                                ),
                                dataManagementNormalViewModel.isOpnedFilter
                                    ? const Icon(Icons.arrow_drop_up_outlined)
                                    : const Icon(Icons.arrow_drop_down),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),

                    // 'isOpendFilter'변수를 참조하여 filter를 표출한다.
                    dataManagementNormalViewModel.isOpnedFilter
                        ? FilterBox(
                            type: 0,
                            checkedFilter:
                                dataManagementNormalViewModel.checkedFilter(),
                            onPressedFilterSave: () =>
                                dataManagementNormalViewModel
                                    .onPressedFilterSave(),
                            /* 조회 기간 */
                            dateList: dataManagementNormalViewModel.dateList,
                            onTapDate: (index) =>
                                dataManagementNormalViewModel.onTapDate(index),
                            dateStatus:
                                dataManagementNormalViewModel.dateStatus,
                            firstDayText:
                                dataManagementNormalViewModel.firstDayText,
                            indexDay: dataManagementNormalViewModel.indexDay,
                            firstDayOnTapTable: () =>
                                dataManagementNormalViewModel.onTapTable(0),
                            lastDayText:
                                dataManagementNormalViewModel.lastDayText,
                            lastDayOnTapTable: () =>
                                dataManagementNormalViewModel.onTapTable(1),
                            isOpenTable:
                                dataManagementNormalViewModel.isOpenTable,
                            focused: dataManagementNormalViewModel.focused,
                            onDaySelected: (selectedDay, focusedDay) =>
                                dataManagementNormalViewModel.onDaySelected(
                                    selectedDay, focusedDay),
                            /* 축종 */
                            speciesList:
                                dataManagementNormalViewModel.speciesList,
                            onTapSpecies: (index) =>
                                dataManagementNormalViewModel
                                    .onTapSpecies(index),
                            speciesStatus:
                                dataManagementNormalViewModel.speciesStatus,
                            /* 정렬 순서 */
                            sortList: dataManagementNormalViewModel.sortList,
                            onTapSort: (index) =>
                                dataManagementNormalViewModel.onTapSort(index),
                            sortStatus:
                                dataManagementNormalViewModel.sortStatus,
                            /* 상태 */
                            statusList:
                                dataManagementNormalViewModel.statusList,
                            onTapstatus: (index) =>
                                dataManagementNormalViewModel
                                    .onTapStatus(index),
                            statusStatus:
                                dataManagementNormalViewModel.statusStatus,
                          )
                        : SizedBox(height: 16.h),

                    // 육류 리스트
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
                            controller:
                                dataManagementNormalViewModel.controller,
                            onChangeFunc: (value) =>
                                dataManagementNormalViewModel.onChanged(value),
                            focusNode: dataManagementNormalViewModel.focusNode,
                            canAlert: false,
                            prefixIcon: const Icon(Icons.search),
                            suffixIcon:
                                dataManagementNormalViewModel.focusNode.hasFocus
                                    ? IconButton(
                                        onPressed: () {
                                          dataManagementNormalViewModel
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
                              dataManagementNormalViewModel.clickedQr(context),
                          icon: const Icon(Icons.qr_code_scanner_rounded),
                        ),
                      ],
                    ),
                    SizedBox(height: 16.h),

                    const CustomTableBar(),
                    SizedBox(height: 16.h),

                    SizedBox(
                      height: 800.h,
                      child: Scrollbar(
                        thumbVisibility: true,
                        controller:
                            dataManagementNormalViewModel.scrollController,
                        child: dataManagementNormalViewModel
                                .selectedList.isEmpty
                            ? Center(
                                child: Text(
                                  '데이터가 없습니다.',
                                  style: Palette.h4Regular,
                                ),
                              )
                            : ListView.separated(
                                controller: dataManagementNormalViewModel
                                    .scrollController,
                                itemCount: dataManagementNormalViewModel
                                    .selectedList.length,
                                itemBuilder: (context, index) => ListCard(
                                  onTap: () async =>
                                      await dataManagementNormalViewModel.onTap(
                                          index, context),
                                  meatId: dataManagementNormalViewModel
                                      .selectedList[index]['meatId']!,
                                  dayTime: dataManagementNormalViewModel
                                      .selectedList[index]['createdAt']!,
                                  statusType: dataManagementNormalViewModel
                                      .selectedList[index]['statusType']!,
                                  dDay: 3 -
                                      Usefuls.calculateDateDifference(
                                        Usefuls.dateShortToDateLong(
                                          dataManagementNormalViewModel
                                                          .selectedList[index]
                                                      ['statusType']! ==
                                                  '반려'
                                              ? dataManagementNormalViewModel
                                                      .selectedList[index]
                                                  ['updatedAt']!
                                              : dataManagementNormalViewModel
                                                      .selectedList[index]
                                                  ['createdAt']!,
                                        ),
                                      ),
                                ),
                                keyboardDismissBehavior:
                                    ScrollViewKeyboardDismissBehavior.onDrag,
                                separatorBuilder:
                                    (BuildContext context, int index) =>
                                        const CustomDivider(),
                              ),
                      ),
                    ),
                    SizedBox(height: 40.h),
                  ],
                ),
              ),
            ),
            dataManagementNormalViewModel.isLoading
                ? const Center(child: LoadingScreen())
                : Container(),
          ],
        ),
      ),
    );
  }
}
