import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/main_input_field.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/my_page/change_password_view_model.dart';

class ChangePasswordScreen extends StatefulWidget {
  const ChangePasswordScreen({
    super.key,
  });

  @override
  State<ChangePasswordScreen> createState() => _ChangePasswordScreenState();
}

class _ChangePasswordScreenState extends State<ChangePasswordScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: const CustomAppBar(
          title: '비밀번호 변경', backButton: true, closeButton: false),
      body: Stack(
        children: [
          GestureDetector(
            onTap: () => FocusScope.of(context).unfocus(),
            child: SingleChildScrollView(
              child: Form(
                key: context.read<ChangePasswordViewModel>().formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    const Row(),
                    SizedBox(
                      height: 72.h,
                    ),
                    Container(
                        margin: EdgeInsets.only(left: 40.w),
                        alignment: Alignment.centerLeft,
                        child: Text('현재 패스워드', style: Palette.fieldTitle)),
                    SizedBox(
                      height: 8.h,
                    ),
                    MainInputField(
                      mode: 1,
                      width: 640.w,
                      formKey: context.read<ChangePasswordViewModel>().formKey,
                      controller:
                          context.read<ChangePasswordViewModel>().originPW,
                      obscureText: true,
                      validateFunc: (value) => context
                          .read<ChangePasswordViewModel>()
                          .pwValidate(value),
                    ),
                    SizedBox(
                      height: 16.h,
                    ),
                    Container(
                        margin: EdgeInsets.only(left: 40.w),
                        alignment: Alignment.centerLeft,
                        child: Text('새 패스워드', style: Palette.fieldTitle)),
                    SizedBox(
                      height: 8.h,
                    ),
                    MainInputField(
                      mode: 1,
                      width: 640.w,
                      formKey: context.read<ChangePasswordViewModel>().formKey,
                      controller: context.read<ChangePasswordViewModel>().newPW,
                      obscureText: true,
                      validateFunc: (value) => context
                          .read<ChangePasswordViewModel>()
                          .newPwValidate(value),
                      hintText: '영문 대/소문자+숫자+특수문자',
                    ),
                    SizedBox(
                      height: 8.h,
                    ),
                    MainInputField(
                      mode: 1,
                      width: 640.w,
                      formKey: context.read<ChangePasswordViewModel>().formKey,
                      controller:
                          context.read<ChangePasswordViewModel>().newCPW,
                      obscureText: true,
                      validateFunc: (value) => context
                          .read<ChangePasswordViewModel>()
                          .cPwValidate(value),
                      hintText: '패스워드 확인',
                    ),
                    SizedBox(
                      height: 600.h,
                    ),
                    MainButton(
                      onPressed:
                          context.watch<ChangePasswordViewModel>().isAllValid()
                              ? () async => context
                                  .read<ChangePasswordViewModel>()
                                  .changePassword(context)
                              : null,
                      text: '저장',
                      width: 658.w,
                      height: 96.h,
                      mode: 1,
                    ),
                  ],
                ),
              ),
            ),
          ),
          context.watch<ChangePasswordViewModel>().isLoading
              ? const Center(
                  child: LoadingScreen(),
                )
              : Container(),
        ],
      ),
    );
  }
}
