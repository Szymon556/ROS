#!/usr/bin/env python3

import message_filters
import rospy
from std_msgs.msg import Int8
from std_msgs.msg import Float32

'''
Program ponizej pobiera docelowa predkosc w rpm oraz aktualna jezeli akutalna
predkosc jest mniejsza od docelowej to zwieksza inkrementacyjnie cs o 1, w przeciwnym razie zmniejsza. 
Tak wiem ze program dziala tylko przy jednym kierunku obrotu silnika.
nie wiem jak mialy by wygladac implementacja kodu zeby sterowala ruchem silnika w przeciwnym kierunku, -10 obrotow na minute jako docelowa predkosc, podane
na set_velocity_goal?
W takim wypadku musialbym przerobic program rpm_counter zeby poradzil sobie z wyliczeniem predkosci gdy silnik kreci sie w przeciwna strone(bo wtedy data.data < prev)
Moja propozycja na ulepszenie tego programu byloby pobieranie wartosci o aktualnym cs silnika i na podstawie tego nim sterowac.
'''


class velocity_controll:
    
    
    def __init__(self) -> None:
        self.actual_rpm = 0
        self.goal_rpm = 0
        self.cs = 0
        self.prev_cs = 0
        self.velocity_goal_subscriber = rospy.Subscriber("/virtual_dc_motor_controller/set_velocity_goal",Float32,callback=self.get_goal_rpm)
        self.velocity_subscriber = rospy.Subscriber("/virtual_dc_motor_driver/get_velocity",Float32,callback=self.calculate)
        self.pub_cs = rospy.Publisher("/virtual_dc_motor/set_cs",Int8,queue_size=10)
#pobierz aktualna predkosc i wysteruj odpowiednio silnik
    def calculate(self,data):
        self.actual_rpm = data.data
        if self.cs <= 100 and self.cs >= 0:#zeby nie wyjsc po za zakres cs
                
            
            if self.actual_rpm < self.goal_rpm:
                self.cs += 1
                self.pub_cs.publish(self.cs)
            elif self.actual_rpm > self.goal_rpm:
               
            
                self.cs = self.cs - 1
                if self.cs < 0:
                   
                   self.cs = 0
                self.pub_cs.publish(self.cs)
            else:
                self.pub_cs.publish(self.cs)
            self.prev_cs = self.cs
        else:#jesli predkosc jes za duza ustaw ostania predkosc(bedzie tutaj maly poslizg i ustawia z reguly maksymalna predkosc)
            self.cs = abs(self.prev_cs)
            if self.goal_rpm < self.actual_rpm:#jesli zmienimy predkosc na mniejsza to sprubuje ja osiagnac.
                self.cs = 0
            self.pub_cs.publish(self.prev_cs)
        #rospy.loginfo(f"self.cs = {self.cs} self.actual_rpm = {self.actual_rpm} self.goal_rpm = {self.goal_rpm} self.actual_rpm.data {data.data}")

    def get_goal_rpm(self,data):#pobierz docelowa predkosc
       
       self.goal_rpm = data.data

    
    
    


    
    

if __name__ == "__main__":
    rospy.init_node("rpm_counter",anonymous=True)
    velocity_controll()
    rospy.spin()