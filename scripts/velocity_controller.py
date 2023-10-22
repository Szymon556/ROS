#!/usr/bin/env python3

import message_filters
import rospy
from std_msgs.msg import Int8
from std_msgs.msg import Float32

'''
Program ponizej pobiera docelowa predkosc w rpm oraz aktualna jezeli akutalna
predkosc jest mniejsza od docelowej to zwieksza inkrementacyjnie cs o 1, w przeciwnym razie zmniejsza. 
if (abs(self.goal_rpm) < abs(self.actual_rpm)) and abs(self.actual_rpm) < 37: ta linijka jest po to
ze gdy ustawimy np rpm 200 co jest poza zakresem silnika (silnik bedzie wtedy utrzymywal maksymalne obroty) a nstepnie damy rpm -10 co juz jest w zakresie pracy silnika
to prgram zeruje cs i ustawia zadana predkosc. 
'''


class velocity_controll:
    
    
    def __init__(self) -> None:
        self.actual_rpm = 0 #aktualne rpm
        self.goal_rpm = 0 #docelowe rpm
        self.cs = 0 #ustawiam controll speed
        self.prev_cs = 0 #zmienna gdy przekroczymy maksymalne rpm dla silnika to ustawiamy ostania poprawna wartosc zeby silnik pracowal w zakresie o -100 do `100`
        self.velocity_goal_subscriber = rospy.Subscriber("/virtual_dc_motor_controller/set_velocity_goal",Float32,callback=self.get_goal_rpm)
        self.velocity_subscriber = rospy.Subscriber("/virtual_dc_motor_driver/get_velocity",Float32,callback=self.calculate)
        self.pub_cs = rospy.Publisher("/virtual_dc_motor/set_cs",Int8,queue_size=10)

#pobierz aktualna predkosc i wysteruj odpowiednio silnik

    def calculate(self,data):
        
        self.actual_rpm = data.data

        if self.cs < 0 and self.actual_rpm > 0: #do obslugi "ujemnych rpm"

                self.actual_rpm = self.actual_rpm * (-1)

        elif self.cs > 0 and self.actual_rpm < 0:
                self.actual_rpm = abs(self.actual_rpm)
        if self.cs < 100 and self.cs > -100:    #zeby nie wyjsc po za zakres cs

            if self.actual_rpm < self.goal_rpm:
                self.cs += 1
            elif self.actual_rpm > self.goal_rpm:
                self.cs = self.cs - 1
            else:
                self.cs = self.prev_cs

            self.prev_cs = self.cs
            self.pub_cs.publish(self.cs)

        else:  
            
            if (abs(self.goal_rpm) < abs(self.actual_rpm)) and abs(self.actual_rpm) < 37:   #jesli zmienimy predkosc na mniejsza to sprubuje ja osiagnac.
                self.cs = 0
            
            self.pub_cs.publish(self.prev_cs)

        #rospy.loginfo(f"self.cs = {self.cs} self.actual_rpm = {self.actual_rpm} self.goal_rpm = {self.goal_rpm} self.actual_rpm.data {data.data}")
        
    def get_goal_rpm(self,data):    #pobierz docelowa predkosc
       
       self.goal_rpm = data.data

    
    
    


    
    

if __name__ == "__main__":

    rospy.init_node("rpm_counter",anonymous=True)
    velocity_controll()
    rospy.spin()
