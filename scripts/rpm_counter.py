#!/usr/bin/env python3

import rospy
from std_msgs.msg import UInt16
from std_msgs.msg import Float32

'''
        W kodzie ponizej licze predkosc katowa na zasadzie: od aktualnej pozycji 
        odejmij poprzednia zeby zobaczysz ile "pozycji/pulsow" wykona enkoder
        w czasie 0.01s (czyli 100hz) nastepnie dziele ta liczbe przez 4096 zeby widziec ile
        drogi przebyl z calosci w tym czasie (czyli 0.01s) a nastepnie mnoze razy 600 zeby miec wynik 
        w minutach. Uwzglednilem tez przypadek gdy roznica miedzy poprzednia pozycja i aktualna praktycznie sie 
        nie zmienia (albo prawie sie nie zmienia) i nastepuje dzielenie przez 0(gdy cs < 13). Z doswiadczen zauwazylem ze <3 jest optymalna wartoscia.
        Rowniez uwzglednilem przypadek gdy wartosc np: prev = 4090 a data.data = 50 to wtedy zeby nie przekalamywac wyniku wyknuje 4096 - prev
        zeby otrzymac prawidlowa odlegosc jaka pokonal silnik podczas 0.01s. Linijka abs(data.data - self.prev) > 4000 jest po ze w przypadku
        gdy cs<13 wartosci na topicu get_position wynosze 0,1,4090 nie wiem dlaczego tak sie dzieje ale ta linijak zapobiega pojawieniu sie 
        absurdalnych wartosci rpm gdy silnik stoji w miesjcu.
'''

class rpm_counter:

    def __init__(self):
       
        self.prev = 0
        self.sub = rospy.Subscriber("/virtual_dc_motor/get_position",UInt16,self.callback)
        self.pub = rospy.Publisher("/virtual_dc_motor_driver/get_velocity",Float32,queue_size=10)

    def callback(self,data):
        
        if abs(data.data - self.prev) <3:
            self.rpm = 0
        elif abs(data.data - self.prev) > 4000:
            self.rpm = 0
        else:
            self.rpm = (abs((data.data-self.prev))/4096) *600
        self.prev = data.data
        rospy.loginfo(f"{self.rpm} {data.data}")
        
        self.pub.publish(self.rpm)
    
   
  
       
    
    

if __name__ == "__main__":
    rospy.init_node("rpm_counter",anonymous=True)
    rpm_counter()
    rospy.spin()
