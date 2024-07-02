import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/main_input_field.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/my_page/user_detail_view_model.dart';

class UserDetailScreen extends StatelessWidget {
  const UserDetailScreen({
    super.key,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => FocusScope.of(context).unfocus(),
      child: Scaffold(
        backgroundColor: Colors.white,
        appBar: const CustomAppBar(
            title: '상세정보 변경', backButton: true, closeButton: false),
        body: Stack(
          children: [
            Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                const Row(),
                SizedBox(
                  height: 40.h,
                ),
                Container(
                    margin: EdgeInsets.only(left: 38.w),
                    alignment: Alignment.centerLeft,
                    child: Text('주소', style: Palette.fieldTitle)),
                SizedBox(
                  height: 8.h,
                ),
                Stack(
                  children: [
                    MainInputField(
                      mode: 1,
                      width: 640.w,
                      controller:
                          context.read<UserDetailViewModel>().mainAddress,
                      readonly: true,
                      hintText: '주소',
                      contentPadding: EdgeInsets.only(left: 30.w, right: 200.w),
                    ),
                    Positioned(
                      right: 30.w,
                      child: TextButton(
                        onPressed: () async => await context
                            .read<UserDetailViewModel>()
                            .clickedSearchButton(context),
                        child: Text(
                          '검색',
                          style: Palette.fieldContent
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
                          .watch<UserDetailViewModel>()
                          .mainAddress
                          .text
                          .isEmpty
                      ? true
                      : false,
                  controller: context.read<UserDetailViewModel>().subAddress,
                  onChangeFunc: (value) => context
                      .read<UserDetailViewModel>()
                      .onChangedSubAdress(value),
                  hintText: '상세주소 (동/호수)',
                ),
                SizedBox(
                  height: 20.h,
                ),
                Container(
                    margin: EdgeInsets.only(left: 38.w),
                    alignment: Alignment.centerLeft,
                    child: Text('회사정보', style: Palette.fieldTitle)),
                SizedBox(
                  height: 8.h,
                ),
                MainInputField(
                  mode: 1,
                  width: 640.w,
                  controller: context.read<UserDetailViewModel>().company,
                  hintText: '회사명',
                  onChangeFunc: (value) => context
                      .read<UserDetailViewModel>()
                      .onChangedCompany(value),
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
                        controller:
                            context.read<UserDetailViewModel>().department,
                        onChangeFunc: (value) => context
                            .read<UserDetailViewModel>()
                            .onChangedDepartment(value),
                        hintText: '부서명',
                      ),
                      const Spacer(),
                      MainInputField(
                        mode: 1,
                        width: 315.w,
                        controller:
                            context.read<UserDetailViewModel>().jobTitle,
                        onChangeFunc: (value) => context
                            .read<UserDetailViewModel>()
                            .onChangedJobTitle(value),
                        hintText: '직위',
                      ),
                    ],
                  ),
                ),
                SizedBox(
                  height: 520.h,
                ),
                Container(
                  margin: EdgeInsets.only(bottom: 40.h),
                  child: MainButton(
                    onPressed:
                        context.watch<UserDetailViewModel>().isActivateButton
                            ? () async {
                                await context
                                    .read<UserDetailViewModel>()
                                    .clickedSaveButton(context);
                              }
                            : null,
                    text: '저장',
                    width: 658.w,
                    height: 106.h,
                    mode: 1,
                  ),
                ),
              ],
            ),
            context.watch<UserDetailViewModel>().isLoading
                ? const Center(child: LoadingScreen())
                : Container(),
          ],
        ),
      ),
    );
  }
}
