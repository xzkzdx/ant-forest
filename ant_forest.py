# -*- coding: utf-8 -*- 
# @Time : 2020/10/15 9:36 
# @Author : 詹生松 
# @File : ant_forest.py
from bin.adb import USBAdb


class AntForest(USBAdb):
    sign = False  #
    ant_forest_text = "蚂蚁森林"
    ant_title = "蚂蚁森林"
    ant_forest_resourceId = "com.alipay.android.phone.openplatform:id/app_text"
    ant_forest_package = package = "com.eg.android.AlipayGphone"
    ant_forest_activity = "com.alipay.mobile.nebulax.integration.mpaas.activity.NebulaActivity$Main"

    def check_ant_forest_page(self):
        if self.app_current["package"] == self.ant_forest_package:
            if self.app_current["activity"] == self.ant_forest_activity:
                return True
        return False

    def wait_in(self, timeout: float = 10.0, **kwargs):
        timeout += self.timestamps()
        while self.package == self.app_current["package"]:
            if self.app_current["activity"] == self.ant_forest_activity:
                if self.elem_find(className="android.widget.Button", text="关闭").exists(5):
                    print("android.widget.Button 关闭")
                    self.elem_find(className="android.widget.Button", text="关闭").click()
                return True
            if self.timestamps() > timeout:
                break
            self.sleep(0.01)
        return False

    def handler(self):
        # self.usb(resourceId="com.alipay.mobile.antui:id/buttomButtonView").click()  # 下一步
        if self.click_elem({
            "text": self.ant_forest_text, "resourceId": self.ant_forest_resourceId
        }, callback=self.wait_in):
            self.collect_energy()

    def collect_energy(self):
        while self.elem_find(resourceId="com.alipay.mobile.nebula:id/h5_tv_title").exists(5):
            if "稍等片刻..." in self.dump_hierarchy:
                continue
            if not self.elem_find(resourceId="J_userEnergy").exists(1):
                continue
            ant_title = self.elem_find(resourceId="com.alipay.mobile.nebula:id/h5_tv_title").info["text"]
            # self.usb.swipe(500, 500, 500, 3000, 0.2)
            x, y, bottom, left, right, top = 0, 0, 0, 0, 0, 0
            if ant_title == self.ant_title and self.elem_find(text="背包").exists(1):
                bottom, left, right, top = self.bounds_position(self.elem_find(text="背包").info)
                x, y = 2 * right - left, top + (bottom - top) // 2
            elif self.elem_find(text="浇水").exists(1):
                bottom, left, right, top = self.bounds_position(self.elem_find(text="浇水").info)
                x, y = 2 * right - left, top + (bottom - top) // 2
            if x <= 0 or y <= 0 or bottom <= 0 or left <= 0 or right <= 0 or top <= 0:
                print("采集结束..., x, y", x, y, bottom, left, right, top)
                break
            if not self.elem_find(resourceId="J_userEnergy").exists(2):
                print("采集结束... J_userEnergy")
                break
            if ant_title == self.ant_title:
                ant_title = "我的" + ant_title
            _bottom, _left, _right, _top = self.bounds_position(self.elem_find(resourceId="J_userEnergy").info)
            _right = self.bounds_position(self.elem_find(text="成就").info)[1] - 50
            _left = _right - 80
            b, l, r, t = int((_top + top) // 2.5), 200, _right - (_right - _left) // 2, 2 * _bottom - _top
            print("开始采集-{}".format(ant_title))
            self._collect_energy(ant_title, b, l, r, t)
            print("结束采集-{}".format(ant_title))
            self.click_xy(x, y)
            self.sleep(2)
            if self.elem_find(resourceId="com.alipay.mobile.nebula:id/h5_tv_title").info["text"] == self.ant_title:
                print("采集结束... J_userEnergy")
                self.usb.press("back")
                break

    def _collect_energy(self, ant_title, bottom, left, right, top, sep=80):
        for x in range(left, right, sep):
            for y in range(top, bottom, sep):
                self.click_xy(x, y)
                self.sleep(0.01)

    def _swipe_to_(self):
        self.usb().swipe("up")
        elem = self.elem_find(text="逛一逛")
        if elem.exists(1):
            bottom, left, right, top = self.bounds_position(elem.info)
            return left + (right - left) // 2, top + (bottom - top) // 2
        return -1, -1


if __name__ == "__main__":
    sn = ""  # adb devices 找到自己的手机id号
    while 1:
        try:
            ant = AntForest(sn)
        except KeyboardInterrupt:
            print("已停止执行")
            break
        except:
            print("重新启动")
