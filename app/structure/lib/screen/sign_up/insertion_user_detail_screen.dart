import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/main_input_field.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/sign_up/insertion_user_detail_view_model.dart';

class InsertionUserDetailScreen extends StatefulWidget {
  const InsertionUserDetailScreen({
    super.key,
  });

  @override
  State<InsertionUserDetailScreen> createState() =>
      _InsertionUserDetailScreenState();
}

class _InsertionUserDetailScreenState extends State<InsertionUserDetailScreen> {
  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        backgroundColor: Colors.white,
        appBar: const CustomAppBar(
            title: '회원가입', backButton: true, closeButton: false),
        body: Stack(
          children: [
            SingleChildScrollView(
              child: Column(
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      SizedBox(
                        height: 40.h,
                      ),
                      Container(
                          margin: EdgeInsets.only(left: 38.w),
                          alignment: Alignment.centerLeft,
                          child: Text('자택주소', style: Pallete.fieldTitle)),
                      SizedBox(
                        height: 8.h,
                      ),
                      Stack(
                        children: [
                          MainInputField(
                            mode: 1,
                            width: 640.w,
                            controller: context
                                .read<InsertionUserDetailViewModel>()
                                .mainAddressController,
                            readonly: true,
                            hintText: '주소',
                            contentPadding:
                                EdgeInsets.only(left: 30.w, right: 200.w),
                          ),
                          Positioned(
                            right: 30.w,
                            child: TextButton(
                              onPressed: () async => context
                                  .read<InsertionUserDetailViewModel>()
                                  .clickedSearchButton(context),
                              child: Text(
                                '검색',
                                style: Pallete.fieldContent
                                    .copyWith(color: Colors.black),
                              ),
                            ),
                          ),
                        ],
                      ),
                      SizedBox(
                        height: 8.h,
                      ),
                      MainInputField(
                        mode: 1,
                        width: 640.w,
                        readonly: context
                                .watch<InsertionUserDetailViewModel>()
                                .mainAddressController
                                .text
                                .isEmpty
                            ? true
                            : false,
                        onChangeFunc: (value) => context
                            .read<InsertionUserDetailViewModel>()
                            .subHomeAdress = value,
                        hintText: '상세주소 (동/호수)',
                      ),
                      SizedBox(
                        height: 20.h,
                      ),
                      Container(
                          margin: EdgeInsets.only(left: 38.w),
                          alignment: Alignment.centerLeft,
                          child: Text('회사 정보', style: Pallete.fieldTitle)),
                      SizedBox(
                        height: 8.h,
                      ),
                      MainInputField(
                        mode: 1,
                        width: 640.w,
                        onChangeFunc: (value) => context
                            .read<InsertionUserDetailViewModel>()
                            .company = value,
                        hintText: '회사명',
                      ),
                      SizedBox(
                        height: 8.h,
                      ),
                      SizedBox(
                        width: 640.w,
                        child: Row(
                          children: [
                            MainInputField(
                              mode: 1,
                              width: 315.w,
                              onChangeFunc: (value) => context
                                  .read<InsertionUserDetailViewModel>()
                                  .department = value,
                              hintText: '부서명',
                            ),
                            const Spacer(),
                            MainInputField(
                              mode: 1,
                              width: 315.w,
                              onChangeFunc: (value) => context
                                  .read<InsertionUserDetailViewModel>()
                                  .jobTitle = value,
                              hintText: '직위',
                            ),
                          ],
                        ),
                      ),
                      SizedBox(
                        height: 460.h,
                      ),
                    ],
                  ),
                  Container(
                    margin: EdgeInsets.only(bottom: 40.h),
                    child: MainButton(
                      onPressed: () async => context
                          .read<InsertionUserDetailViewModel>()
                          .clickedNextButton(context),
                      text: '다음',
                      width: 640.w,
                      height: 96.h,
                      mode: 1,
                    ),
                  ),
                ],
              ),
            ),
            context.watch<InsertionUserDetailViewModel>().isLoading
                ? const Center(
                    child: LoadingScreen(),
                  )
                : Container()
          ],
        ),
      ),
    );
  }
}
