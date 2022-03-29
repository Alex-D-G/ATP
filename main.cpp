#include "hwlib.hpp"

extern "C" int odd(int s);
extern "C" int even(int s);
extern "C" int sommig(int s);
extern "C" int greaterThenFifty(int s);


extern "C" void runTestcases(){
   // Testcase for even()
   if(even(10) == 1 && even(9) == 0 && even(1) == 0 && even(2) == 1){
      hwlib::cout << "even() works correctly! \n";
   }
   else{
      hwlib::cout << "even() works incorrectly \n";
   }

   // Testcase for odd()
   if(odd(10) == 0 && odd(9) == 1 && odd(1) == 1 && odd(2) == 0){
      hwlib::cout << "odd() works correctly! \n";
   }
   else{
      hwlib::cout << "odd() works incorrectly \n";
   }

   // Testcase for sommig()
   if(sommig(1) == 1 && sommig(5) == 15 && sommig(10) == 55 && sommig(20) == 210){
      hwlib::cout << "sommig() works correctly! \n";
   }
   else{
      hwlib::cout << "sommig() works incorrectly \n";
   }

   // Testcase for greaterThenFifty()
   if(greaterThenFifty(20) == 0 && greaterThenFifty(49) == 0 && greaterThenFifty(50) == 0 && greaterThenFifty(51) == 1){
      hwlib::cout << "greaterThenFifty() works correctly! \n";
   }
   else{
      hwlib::cout << "greaterThenFifty() works incorrectly \n";
   }
}

int main( void ){	 
    
   // wait for the PC console to start
   hwlib::wait_ms( 2000 );

   runTestcases();
}
