import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:provider/provider.dart';
import 'package:structure/components/custom_app_bar.dart';
import 'package:structure/components/loading_screen.dart';
import 'package:structure/components/main_button.dart';
import 'package:structure/components/main_input_field.dart';
import 'package:structure/config/pallete.dart';
import 'package:structure/viewModel/my_page/delete_user_view_model.dart';

class DeleteUserScreen extends StatefulWidget {
  const DeleteUserScreen({
    super.key,
  });

  @override
  State<DeleteUserScreen> createState() => _DeleteUserScreenState();
}

class _DeleteUserScreenState extends State<DeleteUserScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: const CustomAppBar(
          title: '회원 탈퇴', backButton: true, closeButton: false),
      body: Stack(
        children: [
          GestureDetector(
            onTap: () => FocusScope.of(context).unfocus(),
            child: SingleChildScrollView(
              child: Form(
                key: context.read<DeleteUserViewModel>().formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    const Row(),
                    SizedBox(height: 72.h),

                    // 비밀번호 입력
                    Container(
                        margin: EdgeInsets.only(left: 40.w),
                        alignment: Alignment.centerLeft,
                        child: Text('비밀번호', style: Palette.fieldTitle)),
                    SizedBox(height: 8.h),

                    // 비밀번호 Input Field
                    MainInputField(
                      mode: 1,
                      width: 640.w,
                      formKey: context.read<DeleteUserViewModel>().formKey,
                      controller: context.read<DeleteUserViewModel>().password,
                      obscureText: true,
                      validateFunc: (value) =>
                          context.read<DeleteUserViewModel>().pwValidate(value),
                    ),

                    SizedBox(height: 820.h),

                    // 회원 탈퇴 버튼
                    MainButton(
                      onPressed: context.watch<DeleteUserViewModel>().isValid()
                          ? () async => context
                              .read<DeleteUserViewModel>()
                              .deleteUser(context)
                          : null,
                      text: '회원 탈퇴',
                      width: 658.w,
                      height: 96.h,
                      mode: 1,
                    ),
                  ],
                ),
              ),
            ),
          ),
          context.watch<DeleteUserViewModel>().isLoading
              ? const Center(child: LoadingScreen())
              : Container(),
        ],
      ),
    );
  }
}
