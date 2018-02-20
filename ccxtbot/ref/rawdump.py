# -*- coding:utf-8 -*-

# -*- coding: utf-8 -*-  
import sys
import traceback
import math
import random
import threading
import socket
import datetime , re , json
import copy
import os
import time
import io , base64
import struct
import platform

oo000 = sys . version_info [ 0 ] >= 3
try :
 import md5
 import urllib2
except :
 import hashlib as md5
 import urllib . request as urllib2

ii = threading . Lock ( )
oOOo = globals ( )
oOOo [ 'NaN' ] = None
oOOo [ 'null' ] = None
oOOo [ 'true' ] = True
oOOo [ 'false' ] = False
O0 = 3000

if oo000 :
 oOOo [ 'xrange' ] = range

if os . getenv ( "BOTVS_TMP_FILE" ) is not None :
 try :
  os . remove ( os . getenv ( "BOTVS_TMP_FILE" ) )
 except :
  pass

class o0O :
 def __init__ ( self , name ) :
  self . __name = name
  sys . modules [ 'talib' ] = self
 def __getattr__ ( self , attr ) :
  raise Exception ( 'Please install %s module for python' % self . __name )

class iI11I1II1I1I ( RuntimeError ) :
 def __init__ ( self , message ) :
  self . message = message

oooo = False
try :
 iIIii1IIi = __import__ ( "talib" )
 import numpy
 oooo = True
except ImportError :
 iIIii1IIi = o0O ( 'talib' )

class o0OO00 ( list ) :
 def __init__ ( self , data ) :
  super ( o0OO00 , self ) . __init__ ( data )
  self . __data = data
 def __getattr__ ( self , attr ) :
  oo = [ ]
  for i1iII1IiiIiI1 in self . __data :
   oo . append ( i1iII1IiiIiI1 [ attr ] )
  if oooo :
   oo = numpy . array ( oo )
  setattr ( self , attr , oo )
  return oo

class iIiiiI1IiI1I1 :
 @ staticmethod
 def _skip ( arr , period ) :
  o0OoOoOO00 = 0
  for I11i in xrange ( 0 , len ( arr ) ) :
   if arr [ I11i ] is not None :
    o0OoOoOO00 += 1
   if o0OoOoOO00 == period :
    break
  return I11i

 @ staticmethod
 def _sum ( arr , num ) :
  O0O = 0.0
  for Oo in xrange ( 0 , num ) :
   if arr [ Oo ] is not None :
    O0O += arr [ Oo ]
  return O0O

 @ staticmethod
 def _avg ( arr , num ) :
  if len ( arr ) == 0 :
   return 0
  O0O = 0.0
  I1ii11iIi11i = 0
  for Oo in xrange ( 0 , min ( len ( arr ) , num ) ) :
   if arr [ Oo ] is not None :
    O0O += arr [ Oo ]
    I1ii11iIi11i += 1
  if I1ii11iIi11i == 0 :
   return 0
  return O0O / I1ii11iIi11i

 @ staticmethod
 def _zeros ( n ) :
  return [ 0.0 ] * n

 @ staticmethod
 def _set ( arr , start , end , value ) :
  for Oo in xrange ( start , min ( len ( arr ) , end ) ) :
   arr [ Oo ] = value

 @ staticmethod
 def _diff ( a , b ) :
  I1IiI = [ None ] * len ( b )
  for Oo in xrange ( 0 , len ( b ) ) :
   if a [ Oo ] is not None and b [ Oo ] is not None :
    I1IiI [ Oo ] = a [ Oo ] - b [ Oo ]
  return I1IiI

 @ staticmethod
 def _move_diff ( a ) :
  I1IiI = [ None ] * ( len ( a ) - 1 )
  for Oo in xrange ( 1 , len ( a ) ) :
   I1IiI [ Oo - 1 ] = a [ Oo ] - a [ Oo - 1 ]
  return I1IiI

 @ staticmethod
 def _cmp ( arr , start , end , cmpFunc ) :
  o0OOO = arr [ start ]
  for Oo in xrange ( start , end ) :
   o0OOO = cmpFunc ( arr [ Oo ] , o0OOO )
  return o0OOO

 @ staticmethod
 def _filt ( records , n , attr , iv , cmpFunc ) :
  if len ( records ) < 2 :
   return None
  o0OOO = iv
  iIiiiI = 0
  if n != 0 :
   iIiiiI = len ( records ) - min ( len ( records ) - 1 , n ) - 1
  for Oo in xrange ( len ( records ) - 2 , iIiiiI - 1 , - 1 ) :
   if records [ Oo ] is not None :
    if attr is not None :
     o0OOO = cmpFunc ( o0OOO , records [ Oo ] [ attr ] )
    else :
     o0OOO = cmpFunc ( o0OOO , records [ Oo ] )
  return o0OOO

 @ staticmethod
 def _ticks ( records ) :
  if len ( records ) == 0 :
   return [ ]

  if isinstance ( records [ 0 ] , int ) or isinstance ( records [ 0 ] , float ) :
   return records

  Iii1ii1II11i = [ None ] * len ( records )
  for Oo in xrange ( 0 , len ( records ) ) :
   Iii1ii1II11i [ Oo ] = records [ Oo ] [ 'Close' ]
  return Iii1ii1II11i

 @ staticmethod
 def _sma ( S , period ) :
  iI111iI = iIiiiI1IiI1I1 . _zeros ( len ( S ) )
  I11i = iIiiiI1IiI1I1 . _skip ( S , period )
  iIiiiI1IiI1I1 . _set ( iI111iI , 0 , I11i , None )
  if I11i < len ( S ) :
   O0O = 0
   for Oo in xrange ( I11i , len ( S ) ) :
    if Oo == I11i :
     O0O = iIiiiI1IiI1I1 . _sum ( S , Oo + 1 )
    else :
     O0O += S [ Oo ] - S [ Oo - period ]
    iI111iI [ Oo ] = O0O / period
  return iI111iI

 @ staticmethod
 def _smma ( S , period ) :
  iI111iI = iIiiiI1IiI1I1 . _zeros ( len ( S ) )
  I11i = iIiiiI1IiI1I1 . _skip ( S , period )
  iIiiiI1IiI1I1 . _set ( iI111iI , 0 , I11i , None )
  if I11i < len ( S ) :
   iI111iI [ I11i ] = iIiiiI1IiI1I1 . _avg ( S , I11i + 1 )
   for Oo in xrange ( I11i + 1 , len ( S ) ) :
    iI111iI [ Oo ] = ( iI111iI [ Oo - 1 ] * ( period - 1 ) + S [ Oo ] ) / period
  return iI111iI

 @ staticmethod
 def _ema ( S , period ) :
  iI111iI = iIiiiI1IiI1I1 . _zeros ( len ( S ) )
  IiII = 2.0 / ( period + 1 )
  I11i = iIiiiI1IiI1I1 . _skip ( S , period )
  iIiiiI1IiI1I1 . _set ( iI111iI , 0 , I11i , None )
  if I11i < len ( S ) :
   iI111iI [ I11i ] = iIiiiI1IiI1I1 . _avg ( S , I11i + 1 )
   for Oo in xrange ( I11i + 1 , len ( S ) ) :
    iI111iI [ Oo ] = ( ( S [ Oo ] - iI111iI [ Oo - 1 ] ) * IiII ) + iI111iI [ Oo - 1 ]
  return iI111iI

class iI1Ii11111iIi :
 @ staticmethod
 def Highest ( records , n , attr = None ) :
  return iIiiiI1IiI1I1 . _filt ( records , n , attr , 5e-324 , max )

 @ staticmethod
 def Lowest ( records , n , attr = None ) :
  return iIiiiI1IiI1I1 . _filt ( records , n , attr , 1.7976931348623157e+308 , min )

 @ staticmethod
 def MA ( records , period = 9 ) :
  return iIiiiI1IiI1I1 . _sma ( iIiiiI1IiI1I1 . _ticks ( records ) , period )

 @ staticmethod
 def SMA ( records , period = 9 ) :
  return iIiiiI1IiI1I1 . _sma ( iIiiiI1IiI1I1 . _ticks ( records ) , period )

 @ staticmethod
 def EMA ( records , period = 9 ) :
  return iIiiiI1IiI1I1 . _ema ( iIiiiI1IiI1I1 . _ticks ( records ) , period )

 @ staticmethod
 def MACD ( records , fastEMA = 12 , slowEMA = 26 , signalEMA = 9 ) :
  Iii1ii1II11i = iIiiiI1IiI1I1 . _ticks ( records )
  i1i1II = iIiiiI1IiI1I1 . _ema ( Iii1ii1II11i , slowEMA )
  O0oo0OO0 = iIiiiI1IiI1I1 . _ema ( Iii1ii1II11i , fastEMA )

  I1i1iiI1 = iIiiiI1IiI1I1 . _diff ( O0oo0OO0 , i1i1II )

  iiIIIII1i1iI = iIiiiI1IiI1I1 . _ema ( I1i1iiI1 , signalEMA )
  o0oO0 = iIiiiI1IiI1I1 . _diff ( I1i1iiI1 , iiIIIII1i1iI )
  return [ I1i1iiI1 , iiIIIII1i1iI , o0oO0 ]

 @ staticmethod
 def BOLL ( records , period = 20 , multiplier = 2 ) :
  oo00 = iIiiiI1IiI1I1 . _ticks ( records )
  I11i = period - 1
  while I11i < len ( oo00 ) and ( oo00 [ I11i ] is None ) :
   I11i += 1
  o00 = iIiiiI1IiI1I1 . _zeros ( len ( oo00 ) )
  Oo0oO0ooo = iIiiiI1IiI1I1 . _zeros ( len ( oo00 ) )
  o0oOoO00o = iIiiiI1IiI1I1 . _zeros ( len ( oo00 ) )
  iIiiiI1IiI1I1 . _set ( o00 , 0 , I11i , None )
  iIiiiI1IiI1I1 . _set ( Oo0oO0ooo , 0 , I11i , None )
  iIiiiI1IiI1I1 . _set ( o0oOoO00o , 0 , I11i , None )
  I1ii11iIi11i = 0.0
  for Oo in xrange ( I11i , len ( oo00 ) ) :
   if Oo == I11i :
    for o0OoOoOO00 in xrange ( 0 , period ) :
     I1ii11iIi11i += oo00 [ o0OoOoOO00 ]
   else :
    I1ii11iIi11i = I1ii11iIi11i + oo00 [ Oo ] - oo00 [ Oo - period ]
   i1 = I1ii11iIi11i / period
   I1IiI = 0
   for o0OoOoOO00 in xrange ( Oo + 1 - period , Oo + 1 ) :
    I1IiI += ( oo00 [ o0OoOoOO00 ] - i1 ) * ( oo00 [ o0OoOoOO00 ] - i1 )
   oOOoo00O0O = math . sqrt ( I1IiI / period )
   i1111 = i1 + ( multiplier * oOOoo00O0O )
   i11 = i1 - ( multiplier * oOOoo00O0O )
   o00 [ Oo ] = i1111
   Oo0oO0ooo [ Oo ] = i1
   o0oOoO00o [ Oo ] = i11
  return [ o00 , Oo0oO0ooo , o0oOoO00o ]

 @ staticmethod
 def KDJ ( records , n = 9 , k = 3 , d = 3 ) :
  I11 = iIiiiI1IiI1I1 . _zeros ( len ( records ) )
  iIiiiI1IiI1I1 . _set ( I11 , 0 , n - 1 , None )
  Oo0o0000o0o0 = iIiiiI1IiI1I1 . _zeros ( len ( records ) )
  oOo0oooo00o = iIiiiI1IiI1I1 . _zeros ( len ( records ) )
  oO0o0o0ooO0oO = iIiiiI1IiI1I1 . _zeros ( len ( records ) )

  oo0o0O00 = iIiiiI1IiI1I1 . _zeros ( len ( records ) )
  oO = iIiiiI1IiI1I1 . _zeros ( len ( records ) )
  for Oo in xrange ( 0 , len ( records ) ) :
   oo0o0O00 [ Oo ] = records [ Oo ] [ 'High' ]
   oO [ Oo ] = records [ Oo ] [ 'Low' ]

  for Oo in xrange ( 0 , len ( records ) ) :
   if Oo >= ( n - 1 ) :
    i1iiIIiiI111 = records [ Oo ] [ 'Close' ]
    oooOOOOO = iIiiiI1IiI1I1 . _cmp ( oo0o0O00 , Oo - ( n - 1 ) , Oo + 1 , max )
    i1iiIII111ii = iIiiiI1IiI1I1 . _cmp ( oO , Oo - ( n - 1 ) , Oo + 1 , min )
    I11 [ Oo ] = ( 100 * ( ( i1iiIIiiI111 - i1iiIII111ii ) / ( oooOOOOO - i1iiIII111ii ) ) ) if oooOOOOO != i1iiIII111ii else 100
    Oo0o0000o0o0 [ Oo ] = float ( 1 * I11 [ Oo ] + ( k - 1 ) * Oo0o0000o0o0 [ Oo - 1 ] ) / k
    oOo0oooo00o [ Oo ] = float ( 1 * Oo0o0000o0o0 [ Oo ] + ( d - 1 ) * oOo0oooo00o [ Oo - 1 ] ) / d
   else :
    Oo0o0000o0o0 [ Oo ] = oOo0oooo00o [ Oo ] = 50.0
    I11 [ Oo ] = 0.0
   oO0o0o0ooO0oO [ Oo ] = 3 * Oo0o0000o0o0 [ Oo ] - 2 * oOo0oooo00o [ Oo ]

  for Oo in xrange ( 0 , n - 1 ) :
   Oo0o0000o0o0 [ Oo ] = oOo0oooo00o [ Oo ] = oO0o0o0ooO0oO [ Oo ] = None
  return [ Oo0o0000o0o0 , oOo0oooo00o , oO0o0o0ooO0oO ]

 @ staticmethod
 def RSI ( records , period = 14 ) :
  I1ii11iIi11i = period
  i1iIIi1 = iIiiiI1IiI1I1 . _zeros ( len ( records ) )
  iIiiiI1IiI1I1 . _set ( i1iIIi1 , 0 , len ( i1iIIi1 ) , None )
  if len ( records ) < I1ii11iIi11i :
   return i1iIIi1

  Iii1ii1II11i = iIiiiI1IiI1I1 . _ticks ( records )
  ii11iIi1I = iIiiiI1IiI1I1 . _move_diff ( Iii1ii1II11i )
  iI111I11I1I1 = ii11iIi1I [ : I1ii11iIi11i ]
  i1111 = 0.0
  OOooO0OOoo = 0.0
  for Oo in xrange ( 0 , len ( iI111I11I1I1 ) ) :
   if iI111I11I1I1 [ Oo ] >= 0 :
    i1111 += iI111I11I1I1 [ Oo ]
   else :
    OOooO0OOoo += iI111I11I1I1 [ Oo ]
  i1111 /= I1ii11iIi11i
  OOooO0OOoo /= I1ii11iIi11i
  OOooO0OOoo = - OOooO0OOoo
  if OOooO0OOoo != 0 :
   iIii1 = i1111 / OOooO0OOoo
  else :
   iIii1 = 0
  i1iIIi1 [ I1ii11iIi11i ] = 100 - 100 / ( 1 + iIii1 )
  oOOoO0 = 0.0
  O0OoO000O0OO = 0.0
  iiI1IiI = 0.0
  for Oo in xrange ( I1ii11iIi11i + 1 , len ( Iii1ii1II11i ) ) :
   oOOoO0 = ii11iIi1I [ Oo - 1 ]
   if oOOoO0 > 0 :
    O0OoO000O0OO = oOOoO0
    iiI1IiI = 0.0
   else :
    O0OoO000O0OO = 0.0
    iiI1IiI = - oOOoO0
   i1111 = ( i1111 * ( I1ii11iIi11i - 1 ) + O0OoO000O0OO ) / I1ii11iIi11i
   OOooO0OOoo = ( OOooO0OOoo * ( I1ii11iIi11i - 1 ) + iiI1IiI ) / I1ii11iIi11i
   iIii1 = 0 if OOooO0OOoo == 0 else ( i1111 / OOooO0OOoo )
   i1iIIi1 [ Oo ] = 100 - 100 / ( 1 + iIii1 )
  return i1iIIi1
 @ staticmethod
 def OBV ( records ) :
  if len ( records ) == 0 :
   return [ ]

  if 'Close' not in records [ 0 ] :
   raise "TA.OBV argument must KLine"

  iI111iI = iIiiiI1IiI1I1 . _zeros ( len ( records ) )
  for Oo in xrange ( 0 , len ( records ) ) :
   if Oo == 0 :
    iI111iI [ Oo ] = records [ Oo ] [ 'Volume' ]
   elif records [ Oo ] [ 'Close' ] >= records [ Oo - 1 ] [ 'Close' ] :
    iI111iI [ Oo ] = iI111iI [ Oo - 1 ] + records [ Oo ] [ 'Volume' ]
   else :
    iI111iI [ Oo ] = iI111iI [ Oo - 1 ] - records [ Oo ] [ 'Volume' ]
  return iI111iI

 @ staticmethod
 def ATR ( records , period = 14 ) :
  if len ( records ) == 0 :
   return [ ]
  if 'Close' not in records [ 0 ] :
   raise "TA.ATR argument must KLine"

  iI111iI = iIiiiI1IiI1I1 . _zeros ( len ( records ) )
  II = 0.0
  I1ii11iIi11i = 0.0
  for Oo in xrange ( 0 , len ( records ) ) :
   ooOoOoo0O = 0
   if Oo == 0 :
    ooOoOoo0O = records [ Oo ] [ 'High' ] - records [ Oo ] [ 'Low' ]
   else :
    ooOoOoo0O = max ( records [ Oo ] [ 'High' ] - records [ Oo ] [ 'Low' ] , abs ( records [ Oo ] [ 'High' ] - records [ Oo - 1 ] [ 'Close' ] ) , abs ( records [ Oo - 1 ] [ 'Close' ] - records [ Oo ] [ 'Low' ] ) )
   II += ooOoOoo0O
   if Oo < period :
    I1ii11iIi11i = II / ( Oo + 1 )
   else :
    I1ii11iIi11i = ( ( ( period - 1 ) * I1ii11iIi11i ) + ooOoOoo0O ) / period
   iI111iI [ Oo ] = I1ii11iIi11i
  return iI111iI

 @ staticmethod
 def Alligator ( records , jawLength = 13 , teethLength = 8 , lipsLength = 5 ) :
  Iii1ii1II11i = [ ]
  for Oo in xrange ( 0 , len ( records ) ) :
   Iii1ii1II11i . append ( ( records [ Oo ] [ 'High' ] + records [ Oo ] [ 'Low' ] ) / 2 )
  return [
 [ None ] * 8 + iIiiiI1IiI1I1 . _smma ( Iii1ii1II11i , jawLength ) ,
  [ None ] * 5 + iIiiiI1IiI1I1 . _smma ( Iii1ii1II11i , teethLength ) ,
  [ None ] * 3 + iIiiiI1IiI1I1 . _smma ( Iii1ii1II11i , lipsLength )
  ]

 @ staticmethod
 def CMF ( records , periods = 20 ) :
  oo = [ ]
  OooO0 = 0.0
  II11iiii1Ii = 0.0
  OO0o = [ ]
  Ooo = [ ]
  for Oo in xrange ( 0 , len ( records ) ) :
   I1IiI = 0.0
   if records [ Oo ] [ 'High' ] != records [ Oo ] [ 'Low' ] :
    I1IiI = ( 2 * records [ Oo ] [ 'Close' ] - records [ Oo ] [ 'Low' ] - records [ Oo ] [ 'High' ] ) / ( records [ Oo ] [ 'High' ] - records [ Oo ] [ 'Low' ] ) * records [ Oo ] [ 'Volume' ]
   OO0o . append ( I1IiI )
   Ooo . append ( records [ Oo ] [ 'Volume' ] )
   OooO0 += I1IiI
   II11iiii1Ii += records [ Oo ] [ 'Volume' ]
   if Oo >= periods :
    OooO0 -= OO0o . pop ( 0 )
    II11iiii1Ii -= Ooo . pop ( 0 )
   oo . append ( OooO0 / II11iiii1Ii )
  return oo


O0o0Oo = { }
Oo00OOOOO = { }
O0OO00o0OO = { }
I11i1 = { }
iIi1ii1I1 = 500

def o0 ( method , firstArg , ret ) :
 global I11i1
 if method not in [
 'Exchange_GetName' ,
 'Exchange_GetLabel' ,
 'Exchange_GetCurrency' ,
 'Exchange_GetBaseCurrency' ,
 'Exchange_GetMinPrice' ,
 'Exchange_GetMinStock' ,
 'Exchange_GetFee' ,
 ] :
  return
 o0OoOoOO00 = '%s_%s' % ( method , firstArg )
 if o0OoOoOO00 not in I11i1 :
  I11i1 [ o0OoOoOO00 ] = ret

def I11II1i ( isStock , ct , customPeriod ) :
 if isStock :
  return [ ]
 oo = [ ]
 IIIII = 0
 if customPeriod == 0 :
  IIIII = 1
 elif customPeriod == 1 :
  IIIII = 3
 elif customPeriod == 2 :
  IIIII = 5
 elif customPeriod == 3 :
  IIIII = 15
 elif customPeriod == 4 :
  IIIII = 30
 elif customPeriod == 5 :
  IIIII = 60
 elif customPeriod == 10 :
  IIIII = 60 * 24
 else :
  return oo

 ooooooO0oo = urllib2 . Request ( 'http://q.botvs.net/chart/history?symbol=%s&resolution=%d' % ( ct , IIIII ) )
 IIiiiiiiIi1I1 = urllib2 . urlopen ( ooooooO0oo )
 I1IIIii = IIiiiiiiIi1I1 . read ( ) . decode ( 'utf8' )

 if not I1IIIii or '[' not in I1IIIii :
  return oo
 oOoOooOo0o0 = json . loads ( I1IIIii )
 for OOOO in oOoOooOo0o0 :
  OOO00 = { }
  OOO00 [ 'Time' ] = int ( OOOO [ 0 ] * 1000 )
  OOO00 [ 'Open' ] = float ( OOOO [ 1 ] )
  OOO00 [ 'High' ] = float ( OOOO [ 2 ] )
  OOO00 [ 'Low' ] = float ( OOOO [ 3 ] )
  OOO00 [ 'Close' ] = float ( OOOO [ 4 ] )
  OOO00 [ 'Volume' ] = float ( OOOO [ 5 ] )
  oo . append ( iiiiiIIii ( OOO00 ) )
 return oo

def O000OO0 ( r , eIndex , platformId , symbol , customPeriod ) :
 o0OoOoOO00 = '%d_%s_%d' % ( eIndex , symbol , customPeriod )

 I11iii1Ii = platformId == "Futures_CTP"
 I1IIiiIiii = platformId == "Futures_LTS"
 O000oo0O = customPeriod == 10
 OOOOi11i1 = O0o0Oo . get ( o0OoOoOO00 , None )
 if ( I11iii1Ii or I1IIiiIiii ) and OOOOi11i1 is None :
  try :
   IIIii1II1II = symbol
   if '_' in symbol :
    IIIii1II1II = symbol . split ( '_' ) [ 1 ]
   OOOOi11i1 = I11II1i ( I1IIiiIiii , IIIii1II1II , customPeriod )
   if OOOOi11i1 is not None and len ( OOOOi11i1 ) > 0 :
    O0o0Oo [ o0OoOoOO00 ] = OOOOi11i1

    Oo00OOOOO [ o0OoOoOO00 ] = { 'Time' : OOOOi11i1 [ - 1 ] [ 'Time' ] , 'Volume' : OOOOi11i1 [ - 1 ] [ 'Volume' ] }
  except :
   pass

 global iIi1ii1I1
 i1I1iI = len ( r )
 if i1I1iI > iIi1ii1I1 :
  iIi1ii1I1 = i1I1iI

 if OOOOi11i1 is not None and len ( OOOOi11i1 ) > 0 :
  oo0OooOOo0 = Oo00OOOOO . get ( o0OoOoOO00 , { 'Time' : 0 , 'Volume' : 0 } )
  o0OO00oO = OOOOi11i1 [ - 1 ]
  for i1iII1IiiIiI1 in r :
   if o0OO00oO [ 'Time' ] == i1iII1IiiIiI1 [ 'Time' ] :
    o0OO00oO [ 'High' ] = max ( o0OO00oO [ 'High' ] , i1iII1IiiIiI1 [ 'High' ] )
    o0OO00oO [ 'Low' ] = min ( o0OO00oO [ 'Low' ] , i1iII1IiiIiI1 [ 'Low' ] )
    o0OO00oO [ 'Close' ] = i1iII1IiiIiI1 [ 'Close' ]
    o0OO00oO [ 'Volume' ] = i1iII1IiiIiI1 [ 'Volume' ]
    if o0OO00oO [ 'Time' ] == oo0OooOOo0 [ 'Time' ] and ( not O000oo0O ) :
     o0OO00oO [ 'Volume' ] += oo0OooOOo0 [ 'Volume' ]
   elif i1iII1IiiIiI1 [ 'Time' ] > o0OO00oO [ 'Time' ] :
    OOOOi11i1 . append ( i1iII1IiiIiI1 )
   if len ( OOOOi11i1 ) > iIi1ii1I1 :
    OOOOi11i1 . pop ( 0 )
  r = OOOOi11i1

 O0o0Oo [ o0OoOoOO00 ] = r
 if oooo :
  r = o0OO00 ( r )
 return r

class I11i1I1I :
 def __init__ ( self , p , index , platformId , currency , period ) :
  self . p = p
  self . currency = currency
  self . platformId = platformId
  self . period = period
  self . index = index
  self . maxKLen = 1000
  self . ct = ''

 def SetContractType ( self , * args ) :
  for IIIii1II1II in args :
   if not IIIii1II1II . startswith ( '-' ) :
    self . ct = IIIii1II1II
    break
  O0OO00o0OO [ self . index ] = self . currency + '_' + self . ct
  return self . p . invoke ( * tuple ( [ 'Exchange_SetContractType' , self . index ] + list ( args ) ) )

 def IO ( self , * args ) :
  if len ( args ) == 2 and args [ 0 ] == 'currency' :
   O0OO00o0OO [ self . index ] = str ( args [ 1 ] ) + '_' + self . ct
  return self . p . invoke ( * tuple ( [ 'Exchange_IO' , self . index ] + list ( args ) ) )

 def Log ( self , logType , orderId = 0 , price = None , amount = None , * extra ) :
  oO0Oo = [ str ( i1iII1IiiIiI1 ) for i1iII1IiiIiI1 in extra ]
  if logType == 2 :
   if amount is not None :
    oO0Oo . insert ( 0 , str ( amount ) )
   if price is not None :
    oO0Oo . insert ( 0 , str ( price ) )
   price = 0.0
   amount = 0.0
  return self . p . invoke ( 'LogRaw' , self . index , orderId , logType , price , amount , ' ' . join ( oO0Oo ) , "" , "" )

 def GetRecords ( self , period = - 1 ) :
  if period == - 1 :
   period = self . period
  oOOoo0Oo = O0OO00o0OO . get ( self . index , '' )
  o00OO00OoO = self . p . invoke ( 'Exchange_GetRecords' , self . index , period )
  if o00OO00OoO is None :
   return o00OO00OoO
  return O000OO0 ( o00OO00OoO , self . index , self . platformId , oOOoo0Oo , period )


 def __getattr__ ( self , name ) :
  if name == 'Go' :
   return lambda * OOOO0OOoO0O0 : self . p . invoke ( 'GoAsync_Exchange_' + OOOO0OOoO0O0 [ 0 ] , self . index , * OOOO0OOoO0O0 [ 1 : ] )
  elif '_' not in name :
   return lambda * OOOO0OOoO0O0 : self . p . invoke ( 'Exchange_' + name , self . index , * OOOO0OOoO0O0 )

 def __repr__ ( self ) :
  return '<Exchange>'

class iiiiiIIii ( dict ) :
 def __getattr__ ( self , name ) :
  if name in self :
   return self [ name ]
  else :
   raise AttributeError ( "no attribute '%s'" % name )

 def __setattr__ ( self , name , value ) :
  self [ name ] = value

 def __delattr__ ( self , name ) :
  if name in self :
   del self [ name ]
  else :
   raise AttributeError ( "no attribute '%s'" % name )

class O0Oo000ooO00 :
 def __init__ ( self , p , config ) :
  self . p = p
  self . p . invoke ( 'Chart_New' , json . dumps ( config ) )

 def add ( self , * arg ) :
  self . p . invoke ( 'Chart_Add' , json . dumps ( list ( arg ) ) )

 def update ( self , config ) :
  self . p . invoke ( 'Chart_New' , json . dumps ( config ) )

 def reset ( self , reverse = 0 ) :
  self . p . invoke ( 'Chart_Reset' , reverse )

 def __repr__ ( self ) :
  return '<Chart>'

class oO0 :
 def __init__ ( self , p , addr , fd ) :
  self . p = p
  self . addr = addr
  self . fd = fd

 def read ( self , timeout = 0 ) :
  return self . p . invoke ( 'TSocket_Read' , self . fd , timeout )

 def write ( self , buf , timeout = 0 ) :
  return self . p . invoke ( 'TSocket_Write' , self . fd , buf , timeout )

 def close ( self ) :
  return self . p . invoke ( 'TSocket_Close' , self . fd )

 def __repr__ ( self ) :
  return '<Dial %s fd:%d>' % ( self . addr , self . fd )

class Ii1iIiII1ii1 :
 def __init__ ( self , p , eIndex , platformId , symbol , period , routineId ) :
  self . p = p
  self . eIndex = eIndex
  self . symbol = symbol
  self . period = period
  self . platformId = platformId
  self . routineId = routineId

 def wait ( self , timeout = - 1 ) :
  o00OO00OoO , ooOooo000oOO = self . p . invoke ( 'GoWait' , self . routineId , timeout )
  if ooOooo000oOO and ( o00OO00OoO is not None ) and self . symbol != '' :
   o00OO00OoO = O000OO0 ( o00OO00OoO , self . eIndex , self . platformId , self . symbol , self . period )
  return o00OO00OoO , ooOooo000oOO

 def __repr__ ( self ) :
  return '<Go %d>' % self . routineId

class Oo0oOOo ( json . JSONEncoder ) :
 def default ( self , obj ) :
  return str ( obj )

Oo0OoO00oOO0o = False
class OOO00O :
 def __init__ ( self , addr , pwd ) :
  self . __addr = addr
  self . __pwd = pwd
  self . __seq = 0
  self . __sock = None
  self . __isConnect = False
  self . __nonce = 0
  if ':' in self . __addr :
   oO0Oo = addr . split ( ':' )
   self . __addr = ( oO0Oo [ 0 ] , int ( oO0Oo [ 1 ] ) )
   self . proto = socket . AF_INET
  else :
   self . __addr = addr
   self . proto = socket . AF_UNIX
  OOoOO0oo0ooO = 0
  O0o0O00Oo0o0 = [ ]
  while True :
   try :
    oo = self . invoke ( 'Exchange_Len' )
    if isinstance ( oo , ( int , float ) ) :
     OOoOO0oo0ooO = oo
     for Oo in xrange ( 0 , OOoOO0oo0ooO ) :
      O0o0O00Oo0o0 . append ( [ - 1 , '' , - 1 ] )
    else :
     OOoOO0oo0ooO = len ( oo )
     O0o0O00Oo0o0 = oo
    break
   except Exception as O00O0oOO00O00 :
    time . sleep ( 1 )
  self . exchanges = [ ]
  self . exchange = None
  for Oo in xrange ( 0 , OOoOO0oo0ooO ) :
   O00O0oOO00O00 = I11i1I1I ( self , Oo + 1 , O0o0O00Oo0o0 [ Oo ] [ 0 ] , O0o0O00Oo0o0 [ Oo ] [ 1 ] , O0o0O00Oo0o0 [ Oo ] [ 2 ] )
   self . exchanges . append ( O00O0oOO00O00 )
   if Oo == 0 :
    self . exchange = O00O0oOO00O00

  if platform . system ( ) == 'Windows' :
   i1Oo00 = threading . Thread ( target = self . wait )
   i1Oo00 . setDaemon ( True )
   i1Oo00 . start ( )

 def wait ( self ) :
  global Oo0OoO00oOO0o
  O0O = socket . socket ( self . proto , socket . SOCK_STREAM )
  try :
   i1i = struct . pack ( "<QBBI" , 2 , 100 , 1 , 0 )
   O0O . connect ( self . __addr )
   O0O . send ( i1i )
   O0O . settimeout ( None )
   O0O . recv ( 5 )
   Oo0OoO00oOO0o = True
  except :
   pass
  O0O . close ( )

 def invoke ( self , method , * arg ) :
  global Oo0OoO00oOO0o , I11i1
  if Oo0OoO00oOO0o :
   Oo0OoO00oOO0o = False
   raise iI11I1II1I1I ( "stop" )
  if method != "_G" and not method [ 0 ] . isupper ( ) :
   raise Exception ( "invalid method" )
  if len ( arg ) > 0 :
   o0OOO = I11i1 . get ( '%s_%s' % ( method , arg [ 0 ] ) , None )
   if o0OOO :
    return o0OOO

  if method == "Dial" :
   method = "TSocket_New"
   if len ( arg ) == 0 :
    arg = ( 30 , )
  if ( method == "Exchange_Buy" or method == "Exchange_Sell" ) and len ( arg ) == 2 :
   arg = ( arg [ 0 ] , - 1 , arg [ 1 ] )
  if oo000 and ( method == "Exchange_CancelOrder" or method == "Exchange_GetOrder" ) and len ( arg ) > 1 and isinstance ( arg [ 1 ] , bytes ) :
   iiI111I1iIiI = list ( arg )
   iiI111I1iIiI [ 1 ] = str ( iiI111I1iIiI [ 1 ] , 'utf-8' )
   arg = tuple ( iiI111I1iIiI )
  ii . acquire ( )
  self . __seq += 1
  IIIi1I1IIii1II = int ( time . time ( ) * 1000000 )
  if IIIi1I1IIii1II <= self . __nonce :
   IIIi1I1IIii1II = self . __nonce + 1
  self . __nonce = IIIi1I1IIii1II
  O0ii1ii1ii = list ( arg )
  for Oo in xrange ( 0 , len ( O0ii1ii1ii ) ) :
   if hasattr ( O0ii1ii1ii [ Oo ] , 'savefig' ) and callable ( O0ii1ii1ii [ Oo ] . savefig ) :
    I1IiI = io . BytesIO ( )
    O0ii1ii1ii [ Oo ] . savefig ( I1IiI , format = "png" )
    O0ii1ii1ii [ Oo ] = '`data:image/png;base64,%s`' % ( base64 . b64encode ( I1IiI . getvalue ( ) ) . decode ( 'utf-8' ) )
   elif isinstance ( O0ii1ii1ii [ Oo ] , dict ) and O0ii1ii1ii [ Oo ] . get ( 'type' ) == 'table' and O0ii1ii1ii [ Oo ] . get ( 'cols' ) :
    O0ii1ii1ii [ Oo ] = '`%s`' % json . dumps ( O0ii1ii1ii [ Oo ] )

  o00OO00OoO = { 'Method' : method , 'Args' : O0ii1ii1ii , 'Nonce' : IIIi1I1IIii1II , 'Sign' : md5 . md5 ( ( method + '|' + str ( IIIi1I1IIii1II ) + '|' + self . __pwd ) . encode ( 'utf-8' ) ) . hexdigest ( ) }
  oooooOoo0ooo = json . dumps ( o00OO00OoO , cls = Oo0oOOo ) . encode ( 'utf-8' )
  i1i = struct . pack ( "<QBBI%ds" % len ( oooooOoo0ooo ) , self . __seq , 100 , 0 , len ( oooooOoo0ooo ) , oooooOoo0ooo )
  if not self . __isConnect :
   self . __sock = socket . socket ( self . proto , socket . SOCK_STREAM )
   self . __sock . connect ( self . __addr )
   self . __sock . settimeout ( None )
   self . __isConnect = True
  try :
   self . __sock . send ( i1i )
  except socket . error as O00O0oOO00O00 :
   self . __isConnect = False
   self . __sock . shutdown ( socket . SHUT_RDWR )
   self . __sock . close ( )
   ii . release ( )
   raise O00O0oOO00O00
  I1I1IiI1 = 13
  III1iII1I1ii = - 1
  oOOo0 = 101
  oo00O00oO = I1I1IiI1
  iIiIIIi = bytes ( )
  while True :
   try :
    iIiIIIi += self . __sock . recv ( oo00O00oO - len ( iIiIIIi ) )
   except socket . error as O00O0oOO00O00 :
    self . __isConnect = False
    self . __sock . shutdown ( socket . SHUT_RDWR )
    self . __sock . close ( )
    ii . release ( )
    raise O00O0oOO00O00
   if len ( iIiIIIi ) >= oo00O00oO :
    if III1iII1I1ii < 0 :
     ooo00OOOooO , oOOo0 , III1iII1I1ii = struct . unpack ( '<QBI' , iIiIIIi [ : I1I1IiI1 ] )
     oo00O00oO += III1iII1I1ii
    else :
     break
  ii . release ( )
  if oOOo0 == 101 :
   try :
    OOOO0OOoO0O0 = str ( iIiIIIi [ I1I1IiI1 : ] . decode ( 'utf-8' ) )
   except :
    OOOO0OOoO0O0 = str ( iIiIIIi [ I1I1IiI1 : ] )
   o00OO00OoO = json . loads ( OOOO0OOoO0O0 , object_hook = iiiiiIIii )
   if len ( o00OO00OoO ) == 1 :
    if method . startswith ( 'Exchange_' ) and len ( arg ) > 0 and o00OO00OoO [ 0 ] is not None :
     o0 ( method , arg [ 0 ] , o00OO00OoO [ 0 ] )
    if method == 'TSocket_New' and o00OO00OoO [ 0 ] is not None :
     return oO0 ( self , arg [ 0 ] , int ( o00OO00OoO [ 0 ] ) )
    elif method . startswith ( 'GoAsync_' ) and o00OO00OoO [ 0 ] is not None :
     O00OOOoOoo0O = ''
     O000OOo00oo = - 1
     oo0OOo = - 1
     oOOoo0Oo = ''
     ooOOO00Ooo = 0
     if len ( arg ) > 0 :
      ooOOO00Ooo = arg [ 0 ]
     if method == 'GoAsync_Exchange_GetRecords' and len ( arg ) > 0 :
      if len ( arg ) == 2 :
       O000OOo00oo = arg [ 1 ]
      if O000OOo00oo == - 1 :
       O000OOo00oo = self . exchanges [ ooOOO00Ooo - 1 ] . period
      oo0OOo = self . exchanges [ ooOOO00Ooo - 1 ] . platformId
      oOOoo0Oo = O0OO00o0OO . get ( ooOOO00Ooo , '' )
     return Ii1iIiII1ii1 ( self , ooOOO00Ooo , oo0OOo , oOOoo0Oo , O000OOo00oo , int ( o00OO00OoO [ 0 ] ) )
    elif ( oo000 and isinstance ( o00OO00OoO [ 0 ] , str ) ) or ( not oo000 ) and isinstance ( o00OO00OoO [ 0 ] , unicode ) :
     return o00OO00OoO [ 0 ] . encode ( 'utf-8' )
    return o00OO00OoO [ 0 ]
   return tuple ( o00OO00OoO )
  if oOOo0 == 102 :
   raise Exception ( iIiIIIi [ I1I1IiI1 : ] )

 def __getattr__ ( self , name ) :
  return lambda * OOOO0OOoO0O0 : self . invoke ( name , * OOOO0OOoO0O0 )

 def __getitem__ ( self , name ) :
  return lambda * OOOO0OOoO0O0 : self . invoke ( name , * OOOO0OOoO0O0 )

 def close ( self ) :
  if self . __sock :
   self . __sock . shutdown ( socket . SHUT_RDWR )
   self . __sock . close ( )

 def Chart ( self , config ) :
  return O0Oo000ooO00 ( self , config )

def IiIIIi1iIi ( date = None , fmt = None ) :
 if date is None :
  date = time . time ( )
 if fmt is None :
  fmt = '%Y-%m-%d %H:%M:%S'
 return time . strftime ( fmt , time . localtime ( date ) )

def ooOOoooooo ( arr1 , arr2 ) :
 if len ( arr1 ) != len ( arr2 ) :
  raise Exception ( "cross array length not equal" )
 I1ii11iIi11i = 0
 for Oo in range ( len ( arr1 ) - 1 , - 1 , - 1 ) :
  if arr1 [ Oo ] is None or arr2 [ Oo ] is None :
   break
  if arr1 [ Oo ] < arr2 [ Oo ] :
   if I1ii11iIi11i > 0 :
    break
   I1ii11iIi11i -= 1
  elif arr1 [ Oo ] > arr2 [ Oo ] :
   if I1ii11iIi11i < 0 :
    break
   I1ii11iIi11i += 1
  else :
   break
 return I1ii11iIi11i

def II1I ( num , precision = 4 ) :
 OOOO0OOoO0O0 = math . pow ( 10 , precision )
 return math . floor ( num * OOOO0OOoO0O0 ) / OOOO0OOoO0O0

def O0i1II1Iiii1I11 ( ns ) :
 global Oo0OoO00oOO0o
 I1ii11iIi11i = float ( ns ) / 1000
 while True :
  if Oo0OoO00oOO0o :
   Oo0OoO00oOO0o = False
   raise iI11I1II1I1I ( "stop" )
  II = min ( I1ii11iIi11i , 0.2 )
  if II <= 0 :
   break
  time . sleep ( II )
  I1ii11iIi11i -= II

def IIII ( ) :
 return False

def iiIiI ( d ) :
 global O0
 if d > 0 :
  O0 = d

def o00oooO0Oo ( pfn , * arg ) :
 while True :
  oo = pfn ( * arg )
  if oo == False or oo is None :
   O0i1II1Iiii1I11 ( O0 )
  else :
   return oo

class o0O0OOO0Ooo :
 pass

iiIiII1 = '''
import os, sys, signal, threading
alreadyExit = False
def exit_handler(signum, frame):
    global alreadyExit
    if alreadyExit:
        return
    alreadyExit = True
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    exitCode = 0
    if 'onexit' in globals():
        t = threading.Thread(target=onexit)
        t.setDaemon(True)
        t.start()
        t.join(timeout=300)
        if t.isAlive():
            exitCode = 1
            sys.stderr.write("onexit timeout")
    os._exit(exitCode)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, exit_handler)
    try:
        if 'init' in globals():
            init()
        if 'main' in globals():
            main()
    except StopError:
        pass
    exit_handler(None, None)
'''

def __init_botvs__ ( rpcAddr , rpcPwd , srcCode ) :
 OOO00O0O = OOO00O ( rpcAddr , rpcPwd )
 o0OOO = { }
 o0OOO [ 'null' ] = None
 o0OOO [ 'true' ] = True
 o0OOO [ 'false' ] = False
 o0OOO [ 'PERIOD_M1' ] = 0
 o0OOO [ 'PERIOD_M3' ] = 1
 o0OOO [ 'PERIOD_M5' ] = 2
 o0OOO [ 'PERIOD_M15' ] = 3
 o0OOO [ 'PERIOD_M30' ] = 4
 o0OOO [ 'PERIOD_H1' ] = 5
 o0OOO [ 'PERIOD_H2' ] = 6
 o0OOO [ 'PERIOD_H4' ] = 7
 o0OOO [ 'PERIOD_H6' ] = 8
 o0OOO [ 'PERIOD_H12' ] = 9
 o0OOO [ 'PERIOD_D1' ] = 10
 o0OOO [ 'PERIOD_D3' ] = 11
 o0OOO [ 'PERIOD_W1' ] = 12
 o0OOO [ 'ORDER_STATE_PENDING' ] = 0
 o0OOO [ 'ORDER_STATE_CLOSED' ] = 1
 o0OOO [ 'ORDER_STATE_CANCELED' ] = 2
 o0OOO [ 'ORDER_STATE_UNKNOWN' ] = 3
 o0OOO [ 'ORDER_TYPE_BUY' ] = 0
 o0OOO [ 'ORDER_TYPE_SELL' ] = 1
 o0OOO [ 'LOG_TYPE_BUY' ] = 0
 o0OOO [ 'LOG_TYPE_SELL' ] = 1
 o0OOO [ 'LOG_TYPE_CANCEL' ] = 2
 o0OOO [ 'PD_LONG' ] = 0
 o0OOO [ 'PD_SHORT' ] = 1
 o0OOO [ 'PD_LONG_YD' ] = 2
 o0OOO [ 'PD_SHORT_YD' ] = 3
 o0OOO [ 'exchange' ] = OOO00O0O . exchange
 o0OOO [ 'exchanges' ] = OOO00O0O . exchanges
 o0OOO [ 'TA' ] = iI1Ii11111iIi
 o0OOO [ 'talib' ] = iIIii1IIi
 o0OOO [ 'Chart' ] = OOO00O0O . Chart
 o0OOO [ '_N' ] = II1I
 o0OOO [ '_Cross' ] = ooOOoooooo
 o0OOO [ '_D' ] = IiIIIi1iIi
 o0OOO [ '_C' ] = o00oooO0Oo
 o0OOO [ '_CDelay' ] = iiIiI
 o0OOO [ 'Sleep' ] = O0i1II1Iiii1I11
 o0OOO [ 'IsVirtual' ] = IIII
 o0OOO [ '__name__' ] = '__main__'
 o0OOO [ 'ext' ] = o0O0OOO0Ooo ( )
 o0OOO [ 'StopError' ] = iI11I1II1I1I

 for o0OoOoOO00 in [ 'Version' , 'Log' , 'LogProfit' , 'LogProfitReset' , 'LogReset' , 'LogStatus' , 'EnableLog' , 'Mail' , 'SetErrorFilter' , 'MD5' , 'HMAC' , 'Hash' , 'UnixNano' , 'GetPid' , 'GetLastError' , '_G' , 'GetCommand' , 'Dial' ] :
  o0OOO [ o0OoOoOO00 ] = OOO00O0O [ o0OoOoOO00 ]
 if oo000 :
  iii = str ( base64 . b64decode ( srcCode ) , 'utf-8' )
 else :
  iii = base64 . b64decode ( srcCode )

 try :
  iiI111I1iIiI = []
  oOooOOOoOo = False
  for i1Iii1i1I in iiI111I1iIiI :
   OOoO00 = copy . copy ( o0OOO )
   for I1ii11iIi11i in i1Iii1i1I [ 1 ] :
    OOoO00 [ I1ii11iIi11i ] = i1Iii1i1I [ 1 ] [ I1ii11iIi11i ]
   if not oOooOOOoOo and 'matplotlib' in i1Iii1i1I [ 0 ] :
    oOooOOOoOo = True
    try :
     __import__ ( 'matplotlib' ) . use ( 'Agg' )
    except :
     pass
   exec ( i1Iii1i1I [ 0 ] + "\n\nif 'init' in locals() and callable(init):\n    init()\n" , OOoO00 )

  iiI111I1iIiI = {"saved_name":"saved_qtum_BTC","use_saved_chushi":true,"first_use_saved_chushi":true,"use_websocket":true,"LoopInterval":1000,"more_than_taolicha":true,"taoli_cha":0.25,"taoli_cha_min":0.2,"taoli_cha_max":1.2,"init_amount":5,"BorE":1,"One_more_learns":500,"delta_delta_U1":65,"huadian":0.000002,"beta_rock":700,"real_time_count":true,"duibi_times_con":40,"qushi_sp":1,"easy_qushi":true,"real_count_fee":true,"jubi_yunbi_cheack_and_change":0.00005,"little_change":2,"price_N":6,"amount_N":2,"is_meet_error_wait":false,"meet_error_wait":200,"cg_delta_speed":2}
  for o0OoOoOO00 in iiI111I1iIiI :
   o0OOO [ o0OoOoOO00 ] = iiI111I1iIiI [ o0OoOoOO00 ]
  if not oOooOOOoOo and 'matplotlib' in iii :
   oOooOOOoOo = True
   try :
    __import__ ( 'matplotlib' ) . use ( 'Agg' )
   except :
    pass
  exec ( iii + "\n\n" + iiIiII1 , o0OOO )
 except :
  IiI111111IIII , i1Ii , ii111iI1iIi1 = sys . exc_info ( )
  oO0Oo = [ OOO for OOO in traceback . extract_tb ( ii111iI1iIi1 ) if OOO [ 0 ] == '<string>' ]
  if oO0Oo :
   oo0OOo0 = [ 'Traceback (most recent call last):\n' ]
   oo0OOo0 = oo0OOo0 + traceback . format_list ( oO0Oo )
  else :
   oo0OOo0 = [ ]
  oo0OOo0 = oo0OOo0 + traceback . format_exception_only ( IiI111111IIII , i1Ii )
  sys . stderr . write ( '' . join ( oo0OOo0 ) )
  exit ( 1 )


__init_botvs__ ( "127.0.0.1:49400" , "URXPDEGFYJDIAEF" , "aW1wb3J0IHRpbWUKaW1wb3J0IHJhbmRvbQppbXBvcnQganNvbgppbXBvcnQgY29weSAgCgppbml0QWNjb3VudCA9IE5vbmUKanlzX2NsYXNzX2xpc3QgPSBbXQppbml0X2RpY3QgPSB7fQppbml0X2RlbHRhID0gMApiYW56aHVhbl9jaGEgPSAwCmxhc3RfYmFuemh1YW5fcHJpY2UgPSAwCnN0cl9mcm96ZW5faWRfanlzID0gWydRdW9pbmUnLCAnQ29pbmNoZWNrJywgJ1phaWYnLCAnSHVvYmknXQojZGVidWfnlKg6IApGRUVfRElDID0geydTZWxsJzogMC4yNSwKICAgICAgICAgICAnQnV5JzogMC4yNSB9CgpGRUVfRElDX09USEVSID0geyAnQml0ZmluZXgnOnsnU2VsbCc6IDAuMiwnQnV5JzogMC4yfSwKICAgICAgICAgICAgICAgICAgJ0tyYWtlbic6eydTZWxsJzogMC4yNiwnQnV5JzogMC4yNn0sCiAgICAgICAgICAgICAgICAgICdIaXRCVEMnOnsnU2VsbCc6IDAuMSwnQnV5JzogMC4xfSwKICAgICAgICAgICAgICAgICAgJ09LQ29pbl9FTic6eydTZWxsJzogMC4yLCdCdXknOiAwLjJ9LAogICAgICAgICAgICAgICAgICdCaW5hbmNlJzp7J1NlbGwnOiAwLjEsJ0J1eSc6IDAuMX0sCiAgICAgICAgICAgICAgICAgJ09LRVgnOnsnU2VsbCc6IDAuMSwnQnV5JzogMC4xfSwKICAgICAgICAgICAgICAgICAnWkInOnsnU2VsbCc6IDAsJ0J1eSc6IDB9LAogICAgICAgICAgICAgICAgICdIdW9iaSc6eydTZWxsJzogMC4yLCdCdXknOiAwLjJ9LAogICAgICAgICAgICAgICAgICdCaXRGbHllcic6eydTZWxsJzogMC4wMSwnQnV5JzogMC4wMX0sCiAgICAgICAgICAgICAgICAnUXVvaW5lJzp7J1NlbGwnOiAwLCdCdXknOiAwfSwKICAgICAgICAgICAgICAgICdDb2luY2hlY2snOnsnU2VsbCc6IDAsJ0J1eSc6IDB9LAogICAgICAgICAgICAgICAgJ1phaWYnOnsnU2VsbCc6IC0wLjAxLCdCdXknOiAtMC4wMX19Cgp3YWl0X2Zvcl9zYXZlZCA9IHsgJ3NhdmVkX2NodXNoaSc6eyAnbW9uZXknOjAsCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgJ2JpJzowLAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICd6Zyc6MCwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAnZmlzdF9wcmljZSc6MCB9LAogICAgICAgICAgICAgICAgICAnc2F2ZWRfZGVsdGEnOnt9LAogICAgICAgICAgICAgICAgICAnc2F2ZWRfYmFuemh1YW4nOmJhbnpodWFuX2NoYSwKICAgICAgICAgICAgICAgICAgJ3NhdmVkX2p5c19maXJzdF9zdGF0ZSc6e319CgppZiB1c2Vfc2F2ZWRfY2h1c2hpIGFuZCBub3QgZmlyc3RfdXNlX3NhdmVkX2NodXNoaToKICAgIHRyeToKICAgICNpZiAxOgogICAgICAgIHRoaXNfc2F2ZWRfbmFtZTEgPSBzYXZlZF9uYW1lICsgJzEnIAogICAgICAgIHRoaXNfc2F2ZWRfbmFtZTIgPSBzYXZlZF9uYW1lICsgJzInCiAgICAKICAgICAgICB3aXRoIG9wZW4oIHRoaXNfc2F2ZWRfbmFtZTEsICdyJykgYXMgZjoKICAgICAgICAgICAgdHJ5OgogICAgICAgICAgICAgICAgc2F2ZWRfZmlsZTEgPSBqc29uLmxvYWQoZikKICAgICAgICAgICAgZXhjZXB0OgogICAgICAgICAgICAgICAgc2F2ZWRfZmlsZTEgPSB7fQogICAgICAgIHdpdGggb3BlbiggdGhpc19zYXZlZF9uYW1lMiwgJ3InKSBhcyBmOgogICAgICAgICAgICB0cnk6CiAgICAgICAgICAgICAgICBzYXZlZF9maWxlMiA9IGpzb24ubG9hZChmKQogICAgICAgICAgICBleGNlcHQ6CiAgICAgICAgICAgICAgICBzYXZlZF9maWxlMiA9IHt9CiAgICAgICAgCiAgICAgICAgaWYgbGVuKHNhdmVkX2ZpbGUxKSA+IGxlbihzYXZlZF9maWxlMik6CiAgICAgICAgICAgIHNhdmVkX2ZpbGUgPSBzYXZlZF9maWxlMQogICAgICAgIGVsc2U6CiAgICAgICAgICAgIHNhdmVkX2ZpbGUgPSBzYXZlZF9maWxlMiAKICAgICAgICAgICAgCiAgICAgICAgY2h1c2hpID0gc2F2ZWRfZmlsZVsnc2F2ZWRfY2h1c2hpJ10gCiAgICAgICAgYmFuemh1YW5fY2hhID0gc2F2ZWRfZmlsZVsnc2F2ZWRfYmFuemh1YW4nXQogICAgICAgIAogICAgICAgIHdhaXRfZm9yX3NhdmVkID0gY29weS5kZWVwY29weSggc2F2ZWRfZmlsZSApCiAgICBleGNlcHQ6CiAgICAgICAgTG9nKCfmnKrmib7liLDliJ3lp4vlrZjmoaPjgIInKQogICAgICAgIAplbHNlOgogICAgY2h1c2hpID0geydtb25leSc6MCwKICAgICAgICAgICAgICAnYmknOjAsCiAgICAgICAgICAgICAgJ3pnJzowLAogICAgICAgICAgICAgICdmaXN0X3ByaWNlJzowfQoKZHVpYmlfcHJpY2UgPSB7J2J1eSc6RmFsc2UsCiAgICAgICAgICAgICAgICdzYWxlJzpGYWxzZSwKICAgICAgICAgICAgICAgJ2NvdW50X3RpbWVzJzowfQoKX0NEZWxheSggMjAwMCApICMg5a656ZSZ6YeN5aSN6L2u6K+i6Ze06ZqUCgpxdXNoaV9hY3Rpb25fc2F2ZSA9IFtdCgoKZGVmIG1haW4oKToKICAgIGdsb2JhbCBjaHVzaGksIHdhaXRfZm9yX3NhdmVkLCBmb3JfdGVzdAogICAgaWYgbGVuKGV4Y2hhbmdlcyk8MjoKICAgICAgICBMb2coZXhjaGFuZ2VzLCflj6rmnInkuI3otrPkv6nvvIzml6Dms5XlpZfliKknKQogICAgZWxzZToKICAgICAgICB0aGlzX2NvbXBhcmVfZGljdCA9IHt9ICPmr5TovoPnlKjnmoTlrZflhbgKICAgICAgICBmb3IgdGhpc19leGNoYW5nZSBpbiBleGNoYW5nZXM6CiAgICAgICAgICAgIGp5cyA9IEpZUyh0aGlzX2V4Y2hhbmdlKQogICAgICAgICAgICBpZiBmaXJzdF91c2Vfc2F2ZWRfY2h1c2hpOgogICAgICAgICAgICAgICAgd2FpdF9mb3Jfc2F2ZWRbJ3NhdmVkX2p5c19maXJzdF9zdGF0ZSddW2p5cy5uYW1lXSA9IHt9CiAgICAgICAgICAgICAgICB3YWl0X2Zvcl9zYXZlZFsnc2F2ZWRfanlzX2ZpcnN0X3N0YXRlJ11banlzLm5hbWVdWydmaXJzdF9CYWxhbmNlJ10gPSBqeXMuZmlyc3RfQmFsYW5jZQogICAgICAgICAgICAgICAgd2FpdF9mb3Jfc2F2ZWRbJ3NhdmVkX2p5c19maXJzdF9zdGF0ZSddW2p5cy5uYW1lXVsnZmlyc3RfYW1vdW50J10gPSBqeXMuZmlyc3RfYW1vdW50CiAgICAgICAgICAgICAgICB3YWl0X2Zvcl9zYXZlZFsnc2F2ZWRfanlzX2ZpcnN0X3N0YXRlJ11banlzLm5hbWVdWyd0cmFkZWRfYW1vdW50J10gPSBqeXMudHJhZGVkX2Ftb3VudAogICAgICAgICAgICBlbHNlOgogICAgICAgICAgICAgICAgdHJ5OgogICAgICAgICAgICAgICAgICAgIHNhdmVkX2ZpbGVbJ3NhdmVkX2p5c19maXJzdF9zdGF0ZSddW2p5cy5uYW1lXQogICAgICAgICAgICAgICAgICAgIGp5cy5maXJzdF9CYWxhbmNlID0gc2F2ZWRfZmlsZVsnc2F2ZWRfanlzX2ZpcnN0X3N0YXRlJ11banlzLm5hbWVdWydmaXJzdF9CYWxhbmNlJ10KICAgICAgICAgICAgICAgICAgICBqeXMuZmlyc3RfYW1vdW50ID0gc2F2ZWRfZmlsZVsnc2F2ZWRfanlzX2ZpcnN0X3N0YXRlJ11banlzLm5hbWVdWydmaXJzdF9hbW91bnQnXQogICAgICAgICAgICAgICAgICAgIGp5cy50cmFkZWRfYW1vdW50ID0gc2F2ZWRfZmlsZVsnc2F2ZWRfanlzX2ZpcnN0X3N0YXRlJ11banlzLm5hbWVdWyd0cmFkZWRfYW1vdW50J10KICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICBMb2coJ+aIkOWKn+S7juWtmOaho+OAkCcsc2F2ZWRfbmFtZSwn44CR5Lit6K+75Y+W5Lqk5piT5omA44CQJyxqeXMubmFtZSwn44CR55qE5Yid5aeL5L+h5oGvJykKICAgICAgICAgICAgICAgIGV4Y2VwdDoKICAgICAgICAgICAgICAgICAgICB3YWl0X2Zvcl9zYXZlZFsnc2F2ZWRfanlzX2ZpcnN0X3N0YXRlJ11banlzLm5hbWVdID0ge30KICAgICAgICAgICAgICAgICAgICB3YWl0X2Zvcl9zYXZlZFsnc2F2ZWRfanlzX2ZpcnN0X3N0YXRlJ11banlzLm5hbWVdWydmaXJzdF9CYWxhbmNlJ10gPSBqeXMuZmlyc3RfQmFsYW5jZQogICAgICAgICAgICAgICAgICAgIHdhaXRfZm9yX3NhdmVkWydzYXZlZF9qeXNfZmlyc3Rfc3RhdGUnXVtqeXMubmFtZV1bJ2ZpcnN0X2Ftb3VudCddID0ganlzLmZpcnN0X2Ftb3VudCAgICAgIAogICAgICAgICAgICAgICAgICAgIHdhaXRfZm9yX3NhdmVkWydzYXZlZF9qeXNfZmlyc3Rfc3RhdGUnXVtqeXMubmFtZV1bJ3RyYWRlZF9hbW91bnQnXSA9IGp5cy50cmFkZWRfYW1vdW50CiAgICAgICAgICAgICAgICAKICAgICAgICAgICAgCiAgICAgICAgICAgICNleGNlcHRfanlzbmFtZXMgPSBbJ0JUQ0MnLCdPS0VYJ10KICAgICAgICAgICAgaWYgdXNlX3dlYnNvY2tldDoKICAgICAgICAgICAgICAgIGV4Y2VwdF9qeXNuYW1lcyA9IFsnQlRDQyddCiAgICAgICAgICAgICAgICBpc193ZWJzb2NrZXQgPSBGYWxzZQogICAgICAgICAgICAjaWYganlzLm5hbWUgaW4gZXhjZXB0X2p5c25hbWVzOgogICAgICAgICAgICAgICAgaWYgbm90IGp5cy5uYW1lIGluIGV4Y2VwdF9qeXNuYW1lczoKICAgICAgICAgICAgICAgICAgICBpc193ZWJzb2NrZXQgPSBqeXMuZXhjaGFuZ2UuSU8oIndlYnNvY2tldCIpCiAgICAgICAgICAgICAgICBpZiBpc193ZWJzb2NrZXQ6CiAgICAgICAgICAgICAgICAgICAganlzLmV4Y2hhbmdlLklPKCJtb2RlIiwgMCkKICAgICAgICAgICAgICAgICAgICBpc193ZWJzb2NrZXQgPSAid2Vic29ja2V0IgogICAgICAgICAgICAgICAgZWxzZToKICAgICAgICAgICAgICAgICAgICBpc193ZWJzb2NrZXQgPSAnUkVTVCcgCiAgICAgICAgICAgIGVsc2U6CiAgICAgICAgICAgICAgICBpc193ZWJzb2NrZXQgPSAnUkVTVCcgCiAgICAgICAgICAgICAgICAKICAgICAgICAgICAganlzLndlYnNvY2tldF9tb2RlID0gaXNfd2Vic29ja2V0IAogICAgICAgICAgICAKICAgICAgICAgICAgTG9nKCflvZPliY3nmoQnLGp5cy5uYW1lLCfnmoRpc193ZWJzb2NrZXTkuLrvvJonLGp5cy53ZWJzb2NrZXRfbW9kZSApCiAgICAgICAgICAgIAogICAgICAgICAgICBqeXNfY2xhc3NfbGlzdC5hcHBlbmQoanlzKQogICAgICAgICAgICB0aGlzX21vbmV5ID0ganlzLmFjY291bnRbJ0JhbGFuY2UnXSArIGp5cy5hY2NvdW50WydGcm96ZW5CYWxhbmNlJ10KICAgICAgICAgICAgdGhpc19zdG9jayA9IGp5cy5hY2NvdW50WydTdG9ja3MnXSArIGp5cy5hY2NvdW50WydGcm96ZW5TdG9ja3MnXQogICAgICAgICAgICAKICAgICAgICAgICAgaWYgbm90IHVzZV9zYXZlZF9jaHVzaGkgb3IgZmlyc3RfdXNlX3NhdmVkX2NodXNoaToKICAgICAgICAgICAgICAgIGNodXNoaVsnbW9uZXknXSArPSB0aGlzX21vbmV5CiAgICAgICAgICAgICAgICBjaHVzaGlbJ2JpJ10gKz0gdGhpc19zdG9jawogICAgICAgICAgICAgICAgY2h1c2hpWyd6ZyddICs9IHRoaXNfbW9uZXkgKyB0aGlzX3N0b2NrICoganlzLlRpY2tlclsnTGFzdCddCiAgICAgICAgaWYgbm90IHVzZV9zYXZlZF9jaHVzaGkgb3IgZmlyc3RfdXNlX3NhdmVkX2NodXNoaTogICAgCiAgICAgICAgICAgIGNodXNoaVsnZmlzdF9wcmljZSddID0gICggY2h1c2hpWyd6ZyddIC0gY2h1c2hpWydtb25leSddICkgLyBjaHVzaGlbJ2JpJ10KICAgICAgICAgICAgZHVpYmlfcHJpY2UgPSByZV9tYWtlX2R1aWJpX2RpYyhqeXNfY2xhc3NfbGlzdCxGYWxzZSxGYWxzZSkKICAgICAgICAgICAgY2h1c2hpWydtYyddID0gbWluKGNodXNoaVsnbW9uZXknXSAsIChjaHVzaGlbJ3pnJ10gLSBjaHVzaGlbJ21vbmV5J10pICkKICAgICAgICAgICAgCiAgICAgICAgICAgIExvZygn5pyq5L2/55So5a2Y5qGj77yM5Yib5bu65paw5a2Y5qGj5Yid5aeL5YC85LitLi4uJykKICAgICAgICAgICAgd2FpdF9mb3Jfc2F2ZWRbJ3NhdmVkX2NodXNoaSddID0gY2h1c2hpIAogICAgICAgICAgICAKICAgICAgICBlbHNlOgogICAgICAgICAgICBMb2coJ+W3suS9v+eUqOWtmOaho++8jOS9v+eUqOWtmOaho+WAvOWIneWni+WMluS4rS4uLicpCiAgICAgICAgICAgIAogICAgICAgIExvZygn5Yid5aeL5oC76ZKx5Li677yaJyxfTiggY2h1c2hpWydtb25leSddLCBwcmljZV9OICksJ+WIneWni+aAu+W4geaVsOmHj+S4uicsX04oIGNodXNoaVsnYmknXSwgYW1vdW50X04gKSwKICAgICAgICAgICAgJ+WIneWni+S7k+aAu+WAvOS4uicsX04oIGNodXNoaVsnemcnXSwgcHJpY2VfTiApLCfliJ3lp4vnmoTkuqTmmJPmiYDlubPlnYfku7fmoLzkuLrvvJonLF9OKCBjaHVzaGlbJ2Zpc3RfcHJpY2UnXSwgcHJpY2VfTikgKQogICAgICAgIAogICAgICAgIGp5c19jb21wYXJlX2xpc3QgPSBtYWtlX2NvbXBhcmVfZGljdChqeXNfY2xhc3NfbGlzdCkgI+aJvuWHuuaJgOacieS6pOaYk+aJgOmFjeWvue+8jOS4jemHjeWkjeOAggogICAgICAgIAogICAgICAgIAogICAgICAgIGZvciBpIGluIGp5c19jb21wYXJlX2xpc3Q6CiAgICAgICAgICAgIHRyeToKICAgICAgICAgICAgICAgIHdhaXRfZm9yX3NhdmVkWydzYXZlZF9kZWx0YSddIAogICAgICAgICAgICBleGNlcHQ6CiAgICAgICAgICAgICAgICB3YWl0X2Zvcl9zYXZlZFsnc2F2ZWRfZGVsdGEnXSA9IHt9CiAgICAgICAgICAgIHRyeToKICAgICAgICAgICAgICAgIHdhaXRfZm9yX3NhdmVkWydzYXZlZF9kZWx0YSddW2lbMF0ubmFtZV0KICAgICAgICAgICAgZXhjZXB0OgogICAgICAgICAgICAgICAgd2FpdF9mb3Jfc2F2ZWRbJ3NhdmVkX2RlbHRhJ11baVswXS5uYW1lXSA9IHt9CiAgICAgICAgICAgIHRyeToKICAgICAgICAgICAgICAgIHdhaXRfZm9yX3NhdmVkWydzYXZlZF9kZWx0YSddW2lbMF0ubmFtZV1baVsxXS5uYW1lXQogICAgICAgICAgICBleGNlcHQ6CiAgICAgICAgICAgICAgICB3YWl0X2Zvcl9zYXZlZFsnc2F2ZWRfZGVsdGEnXVtpWzBdLm5hbWVdW2lbMV0ubmFtZV0gPSB7fQogICAgICAgICAgICAKICAgICAgICAgICAgaWYgdXNlX3NhdmVkX2NodXNoaSBhbmQgbm90IGZpcnN0X3VzZV9zYXZlZF9jaHVzaGk6CiAgICAgICAgICAgICAgICB0cnk6CiAgICAgICAgICAgICAgICAgICAgaVswXS5kZWx0YV9pbml0KCBpWzFdICwgaW5pdF9kZWx0YSApCiAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgaVswXS5kZWx0YV9saXN0W2lbMV0ubmFtZV0gPSBzYXZlZF9maWxlWydzYXZlZF9kZWx0YSddW2lbMF0ubmFtZV1baVsxXS5uYW1lXVsnZGVsdGFfbGlzdCddCiAgICAgICAgICAgICAgICAgICAgaVswXS5kZWx0YV9jZ19saXN0W2lbMV0ubmFtZV0gPSBzYXZlZF9maWxlWydzYXZlZF9kZWx0YSddW2lbMF0ubmFtZV1baVsxXS5uYW1lXVsnZGVsdGFfY2dfbGlzdCddCiAgICAgICAgICAgICAgICAgICAgaVswXS50cmFkZWRfdGltZXNfZGljdFtpWzFdLm5hbWVdID0gc2F2ZWRfZmlsZVsnc2F2ZWRfZGVsdGEnXVtpWzBdLm5hbWVdW2lbMV0ubmFtZV1bJ3RyYWRlZF90aW1lcyddCiAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICBleGNlcHQ6CiAgICAgICAgICAgICAgICAgICAgaVswXS5kZWx0YV9pbml0KCBpWzFdICwgaW5pdF9kZWx0YSApCgogICAgICAgICAgICAgICAgICAgIGlbMF0uZGVsdGFfbGlzdFtpWzFdLm5hbWVdID0gc2F2ZWRfZmlsZVsnc2F2ZWRfZGVsdGEnXVtpWzFdLm5hbWVdW2lbMF0ubmFtZV1bJ2RlbHRhX2xpc3QnXQogICAgICAgICAgICAgICAgICAgIGlbMF0uZGVsdGFfY2dfbGlzdFtpWzFdLm5hbWVdID0gc2F2ZWRfZmlsZVsnc2F2ZWRfZGVsdGEnXVtpWzFdLm5hbWVdW2lbMF0ubmFtZV1bJ2RlbHRhX2NnX2xpc3QnXQogICAgICAgICAgICAgICAgICAgIGlbMF0udHJhZGVkX3RpbWVzX2RpY3RbaVsxXS5uYW1lXSA9IHNhdmVkX2ZpbGVbJ3NhdmVkX2RlbHRhJ11baVsxXS5uYW1lXVtpWzBdLm5hbWVdWyd0cmFkZWRfdGltZXMnXQogICAgICAgICAgICBlbHNlOgogICAgICAgICAgICAgICAgaVswXS5kZWx0YV9pbml0KCBpWzFdICwgaW5pdF9kZWx0YSApCgogICAgICAgICAgICAgICAgd2FpdF9mb3Jfc2F2ZWRbJ3NhdmVkX2RlbHRhJ11baVswXS5uYW1lXVtpWzFdLm5hbWVdWyd0cmFkZWRfdGltZXNfZGljdCddID0gaVswXS50cmFkZWRfdGltZXNfZGljdFtpWzFdLm5hbWVdCiAgICAgICAgICAgICAgICB3YWl0X2Zvcl9zYXZlZFsnc2F2ZWRfZGVsdGEnXVtpWzBdLm5hbWVdW2lbMV0ubmFtZV1bJ2RlbHRhX2xpc3QnXSA9IGlbMF0uZGVsdGFfbGlzdFtpWzFdLm5hbWVdCiAgICAgICAgICAgICAgICB3YWl0X2Zvcl9zYXZlZFsnc2F2ZWRfZGVsdGEnXVtpWzBdLm5hbWVdW2lbMV0ubmFtZV1bJ2RlbHRhX2NnX2xpc3QnXSA9IGlbMF0uZGVsdGFfY2dfbGlzdFtpWzFdLm5hbWVdICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgCiAgICAgICAgICAgIAogICAgICAgICAgICAKICAgIGxhc3RfbG9vcF90aW1lID0gdGltZS50aW1lKCkgICAgCiAgICBjaXNodSA9IDAKICAgIHNob3VsZF9zaG93ID0gMAogICAgdGhpc19mb3JjZV95aW5nbGlfbTIgPSAwCiAgICBsYXN0XzEwMDBfanlfYW1vdW50ID0gMAogICAgbGFzdF8xMDAwX2p5X2Ftb3VudF9jaXNodSA9IDAKICAgIHRpbWVzX2NvbiA9IDI4OCAqIGxlbihqeXNfY2xhc3NfbGlzdCkKICAgICNMb2coanlzX2xpc3QpCiAgICBpc190cmFkZWRfbGFzdCA9IDAgCiAgICBxdWFyeV9tb3JlID0gT25lX21vcmVfbGVhcm5zCiAgICBUYWJsZU1hbmFnZXIsICB0YWJsZV8xLCB0YWJsZV8yID0gY3JlYXRlX3RoZV90YWJsZSgganlzX2NsYXNzX2xpc3QgLCBqeXNfY29tcGFyZV9saXN0ICkKICAgICNMb2dQcm9maXRSZXNldCgxKSAjIOeUqOadpea4heepuuWbvgogICAgd2hpbGUoMSk6CiAgICAgICAgIyDkuK3pl7TnmoTku4XkvZzmtYvor5XnlKjvvIzmraPlvI/niYjor7fms6jph4rmjokKICAgICAgICBmb3JfdGVzdCA9IGNpc2h1CiAgICAgICAgIyDkuK3pl7TnmoTku4XkvZzmtYvor5XnlKjvvIzmraPlvI/niYjor7fms6jph4rmjokKICAgICAgICB0aGlzX2xvb3BfdGltZSA9IHRpbWUudGltZSgpCiAgICAgICAgdGhpc190aW1lX2NoYSA9IHRoaXNfbG9vcF90aW1lIC0gbGFzdF9sb29wX3RpbWUKICAgICAgICBsYXN0X2xvb3BfdGltZSA9IHRoaXNfbG9vcF90aW1lCiAgICAgICAgaWYgdGhpc190aW1lX2NoYSoxMDAwID4gMCBhbmQgdGhpc190aW1lX2NoYSAqMTAwMDwgTG9vcEludGVydmFsOgogICAgICAgICAgICBTbGVlcChMb29wSW50ZXJ2YWwpCiAgICAgICAgCiAgICAgICAgbW9yZV9zbGVlcCA9IEZhbHNlCiAgICAgICAgc2hvdWxkX3Nob3cgKz0gMQogICAgICAgIGNpc2h1ICs9IDEKICAgICAgICBsYXN0XzEwMDBfanlfYW1vdW50X2Npc2h1ICs9IDEKICAgICAgICAKICAgICAgICBtYWtlX2RhdGFfc2F2ZWQoIHdhaXRfZm9yX3NhdmVkLCBjaHVzaGksIGp5c19jb21wYXJlX2xpc3QsIGJhbnpodWFuX2NoYSkgI+i/meS4quWHveaVsOeUqOadpeWCqOWtmOS/oeaBrwogICAgICAgIAogICAgICAgIGZvciB0aGlzX2p5cyBpbiBqeXNfY2xhc3NfbGlzdDoKICAgICAgICAgICAgCiAgICAgICAgICAgIGlmIGlzX21lZXRfZXJyb3Jfd2FpdDoKICAgICAgICAgICAgICAgICPmmK/lkKbpnIDopoHnm5HmtYvplJnor6/ljZXvvJ8KICAgICAgICAgICAgICAgIGFmdGVyX3RyYWRlX2RvX2NoZWNrKCB0aGlzX2p5cyApCiAgICAgICAgICAgICAgICBpZiB0aGlzX2p5cy5lcnJvcl93YWl0ID4wOgogICAgICAgICAgICAgICAgICAgIHRoaXNfanlzLmVycm9yX3dhaXQgLT0gMQogICAgICAgICAgICAgICAgICAgIGlmIGp5cy5lcnJvcl93YWl0ICU5OSA9PSAxOgogICAgICAgICAgICAgICAgICAgICAgICBMb2coJ+eUseS6juS5i+WJjScsIGp5cy5uYW1lLCAn5Ye6546w5LqG6ZSZ6K+vLOi/meS4quS6pOaYk+aJgOWwhuWcqO+8micsanlzLmVycm9yX3dhaXQgKzEgLCfmrKHova7or6LlkI7lho3lj4LkuI7kuqTmmJPjgIInKQogICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICBpZiBjaXNodSUgNTAgPT0gMToKICAgICAgICAgICAgICAgIHRoaXNfanlzLmFjY291bnRfc3RhdGUgPSAnd2FpdF9mb3JfcmVmcmVzaF9yZCcgICAgICAgIAogICAgICAgICAgICAgICAgCiAgICAgICAgdHJ5OgogICAgICAgICNpZiAxOgogICAgICAgICAgICBpZiBjaXNodSAlIDk5ID09IDE6CiAgICAgICAgICAgICAgICBpc190cmFkZWRfbGFzdCA9IGRlbF93aXRoX2Zyb3plbihqeXNfY2xhc3NfbGlzdCwgbm93X21iLCBlYXN5X3F1c2hpLGNodXNoaSApCiAgICAgICAgZXhjZXB0OgogICAgICAgICAgICBwYXNzICAgICAgICAKICAgICAgICAKICAgICAgICAKICAgICAgICBpZiBjaXNodSA+IGR1aWJpX3RpbWVzX2NvbiArIE9uZV9tb3JlX2xlYXJuczoKICAgICAgICAgICAgI0xvZygn6LaL5Yq/5py65ZCv5Yqo5LitJykKICAgICAgICAgICAgI2lmIDE6CiAgICAgICAgICAgIHRyeToKICAgICAgICAgICAgICAgIGJ1Y2FuZyhqeXNfY2xhc3NfbGlzdCAsIG5vd19tYiAsIGNodXNoaSwgY2lzaHUsIGVhc3lfcXVzaGkpCiAgICAgICAgICAgIGV4Y2VwdDoKICAgICAgICAgICAgICAgIHBhc3MKICAgICAgICAgICAgCiAgICAgICAgY2xlYW5fZGF0YShqeXNfY2xhc3NfbGlzdCkKICAgICAgICBnZXRfZGF0YShqeXNfY2xhc3NfbGlzdCwganlzX2NvbXBhcmVfbGlzdCwgY2lzaHUpCiAgICAgICAgYWxsX3RyYWRlX2RpY3QgPSBtYWtlX3RyYWRlX2RpY3QoanlzX2NvbXBhcmVfbGlzdCkKCiAgICAgICAgaWYgbGFzdF8xMDAwX2p5X2Ftb3VudF9jaXNodSA+IHRpbWVzX2NvbjoKICAgICAgICAgICAgI+avj3RpbWVzX2Nvbuasoei9ruivouajgOafpeS4gOasoeW9k+WJjeaYr+WQpuW6lOivpeiwg+S8mHRhb2xpY2hhCiAgICAgICAgICAgIGxhc3RfMTAwMF9qeV9hbW91bnQsIGxhc3RfMTAwMF9qeV9hbW91bnRfY2lzaHUgPSBhdXRvX2NoYW5nZV90YW9saWNoYShsYXN0XzEwMDBfanlfYW1vdW50LCBsYXN0XzEwMDBfanlfYW1vdW50X2Npc2h1KSAj6L+Z5Liq55So5p2l6Ieq5Yqo5o6n5Yi25aWX5Yip5beu55qE5b2T5YmN5YC8CiAgICAgICAgCiAgICAgICAgaWYgbGVuKGFsbF90cmFkZV9kaWN0KT4wIGFuZCBjaXNodSA+IHF1YXJ5X21vcmUgOgogICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgc29ydGVkX3RyYWRlX2xpc3QgPSBzb3J0ZWQoYWxsX3RyYWRlX2RpY3QsIGtleT1sYW1iZGEgazoga1snamlhY2hhJ10sIHJldmVyc2U9VHJ1ZSkKICAgICAgICAgICAgCiAgICAgICAgICAgIGxhc3RfZG9uZV9hbW91bnQgPSAwCiAgICAgICAgICAgIGZvciB0aGlzX3RyYWRlIGluIHNvcnRlZF90cmFkZV9saXN0OgogICAgICAgICAgICAgICAgdHJ5OgogICAgICAgICAgICAgICAgICAgIGJ1eV9qeXNfc3RvY2sgPSB0aGlzX3RyYWRlWydidXlfanlzJ10uYWNjb3VudFsnU3RvY2tzJ10KICAgICAgICAgICAgICAgICAgICBzYWxlX2p5c19zdG9jayA9IHRoaXNfdHJhZGVbJ3NhbGVfanlzJ10uYWNjb3VudFsnU3RvY2tzJ10KICAgICAgICAgICAgICAgICAgICBidXlfanlzID0gdGhpc190cmFkZVsnYnV5X2p5cyddCiAgICAgICAgICAgICAgICAgICAgc2FsZV9qeXMgPSB0aGlzX3RyYWRlWydzYWxlX2p5cyddCiAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgaWYgc2FsZV9qeXNfc3RvY2sgPiBidXlfanlzX3N0b2NrLzIwIGFuZCBzYWxlX2p5c19zdG9jayA+IEJvckU6CiAgICAgICAgICAgICAgICAgICAgICAgIGlmIGJ1eV9qeXMuZXJyb3Jfd2FpdCA+IDA6CiAgICAgICAgICAgICAgICAgICAgICAgICAgICBidXlfanlzLmVycm9yX3dhaXQgLT0gMQogICAgICAgICAgICAgICAgICAgICAgICAgICAgaWYgYnV5X2p5cy5lcnJvcl93YWl0ICUzNyA9PSAxOgogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIExvZygn55Sx5LqO5LmL5YmNJywgYnV5X2p5cy5uYW1lLCAn5Ye6546w5LqG6ZSZ6K+vLOi/meS4quS6pOaYk+aJgOWwhuWcqO+8micsCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIGJ1eV9qeXMuZXJyb3Jfd2FpdCArMSAsJ+asoei9ruivouWQjuWGjeWPguS4juS6pOaYk+OAgicpCiAgICAgICAgICAgICAgICAgICAgICAgIGVsaWYgc2FsZV9qeXMuZXJyb3Jfd2FpdCA+IDA6CiAgICAgICAgICAgICAgICAgICAgICAgICAgICBzYWxlX2p5cy5lcnJvcl93YWl0IC09IDEKICAgICAgICAgICAgICAgICAgICAgICAgICAgIGlmIHNhbGVfanlzLmVycm9yX3dhaXQgJTM3ID09IDE6CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgTG9nKCfnlLHkuo7kuYvliY0nLCBzYWxlX2p5cy5uYW1lLCAn5Ye6546w5LqG6ZSZ6K+vLOi/meS4quS6pOaYk+aJgOWwhuWcqO+8micsCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIHNhbGVfanlzLmVycm9yX3dhaXQgKzEgLCfmrKHova7or6LlkI7lho3lj4LkuI7kuqTmmJPjgIInKQogICAgICAgICAgICAgICAgICAgICAgICBlbHNlOgogICAgICAgICAgICAgICAgICAgICAgICAgICAgdGhpc190cmFkZVsnc2hvdWxkX2xlc3NfdGhhbl9saXN0J11bMF0gPSBtYXgoIHRoaXNfdHJhZGVbJ3Nob3VsZF9sZXNzX3RoYW5fbGlzdCddWzBdIC0gbGFzdF9kb25lX2Ftb3VudCwwICkKICAgICAgICAgICAgICAgICAgICAgICAgICAgIHRoaXNfdHJhZGVbJ3Nob3VsZF9sZXNzX3RoYW5fbGlzdCddWzFdID0gbWF4KCB0aGlzX3RyYWRlWydzaG91bGRfbGVzc190aGFuX2xpc3QnXVsxXSAtIGxhc3RfZG9uZV9hbW91bnQsMCApCiAgICAgICAgICAgICAgICAgICAgICAgICAgICB0aGlzX3RyYWRlWydzaG91bGRfbGVzc190aGFuJ10gPSBtaW4odGhpc190cmFkZVsnc2hvdWxkX2xlc3NfdGhhbl9saXN0J10pCiAgICAgICAgICAgICAgICAgICAgICAgICAgICB0aGlzX3RyYWRlX09hbW91bnQgPSBsZXRfdXNfdHJhZGUodGhpc190cmFkZSkKICAgICAgICAgICAgICAgICAgICAgICAgICAgIGxhc3RfZG9uZV9hbW91bnQgPSBsYXN0X2RvbmVfYW1vdW50IC0gdGhpc190cmFkZV9PYW1vdW50CiAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgIGxhc3RfMTAwMF9qeV9hbW91bnQgKz0gdGhpc190cmFkZV9PYW1vdW50CiAgICAgICAgICAgICAgICAgICAgICAgICAgICBpc190cmFkZWRfbGFzdCA9IDMwCgogICAgICAgICAgICAgICAgZXhjZXB0OgogICAgICAgICAgICAgICAgICAgIHBhc3MKICAgICAgICBlbHNlOgogICAgICAgICAgICBpZiBjaXNodSA+IE9uZV9tb3JlX2xlYXJucyA6CiAgICAgICAgICAgICAgICBpZiBjaXNodSUxMDAwID09MCA6CiAgICAgICAgICAgICAgICAgICAgTG9nKCflt7Lnu4/op4Llr5/lpKfnm5jovr7liLDmjIflrprmrKHmlbDvvIzlpoLmnpznm5HmtYvliLDmnInliKnlt67vvIzlsIblvIDlp4vlpZfliKnjgILlvZPliY3ova7or6LmrKHmlbDkuLrvvJonLGNpc2h1KQogICAgICAgICAgICAgICAgZWxpZiBxdWFyeV9tb3JlID4gY2lzaHUgOgogICAgICAgICAgICAgICAgICAgIGlmICggcXVhcnlfbW9yZSAtIGNpc2h1ICklMzMgPT0gMToKICAgICAgICAgICAgICAgICAgICAgICAgTG9nKCfkuqTmmJPnrYnlvoXkuK3vvIzov5jmnIknLCBxdWFyeV9tb3JlIC0gY2lzaHUgLCfmrKHph43mlrDlvIDlp4vkuqTmmJPjgIInKQogICAgICAgICAgICAgICAgZWxpZiBxdWFyeV9tb3JlID09IGNpc2h1OgogICAgICAgICAgICAgICAgICAgIExvZygn5bey57uP6YeN5paw562J5b6F5LqGMzAw5qyh77yM5oiR5Lus5o6l552A5Lqk5piT44CCJykKICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgZWxpZiBjaXNodSU0MCA9PSAxIDoKICAgICAgICAgICAgICAgIExvZygn5b2T5YmN56ysJyxjaXNodSwn5qyh77yM6L+Y5pyJJyxPbmVfbW9yZV9sZWFybnMgLWNpc2h1LCfmrKHop4Llr5/nm5jlkI7lvIDlp4vkuqTmmJPjgIInICkKICAgICAgICAgICAgZWxpZiBjaXNodSA9PSBPbmVfbW9yZV9sZWFybnM6CiAgICAgICAgICAgICAgICBMb2coJ+W3sue7j+inguWvn+Wkp+ebmOi+vuWIsOaMh+WumuasoeaVsO+8jOeOsOWcqOW8gOWni++8jOWmguaenOajgOa1i+WIsOWIqeW3ru+8jOWImeW8gOWni+S6pOaYk+OAguW9k+WJjei9ruivouasoeaVsOS4uu+8micsY2lzaHUpCiAgICAgICAgICAgIAogICAgICAgICAgICAKICAgICAgICBpZiBtb3JlX3NsZWVwIGFuZCBMb29wSW50ZXJ2YWw8MTAwMDoKICAgICAgICAgICAgU2xlZXAoMTAwMCkKICAgICAgICB0cnk6CiAgICAgICAgI+WxleekuuWxggogICAgICAgICNpZigxKToKICAgICAgICAgICAgVGFibGVNYW5hZ2VyID0gbWFrZV90YWJsZV93aXRoICggVGFibGVNYW5hZ2VyICwgIHRhYmxlXzEgLCB0YWJsZV8yICwganlzX2NsYXNzX2xpc3QgLCBqeXNfY29tcGFyZV9saXN0ICkKICAgICAgICAgICAgbm93X21iID0gIHsnbW9uZXknOjAsCiAgICAgICAgICAgICAgICAgICAgICAgJ2JpJzowLAogICAgICAgICAgICAgICAgICAgICAgICd6Zyc6MCwKICAgICAgICAgICAgICAgICAgICAgICAncGluZ2p1bl9wcmljZSc6MH0KICAgICAgICAgICAgCiAgICAgICAgICAgIF9udW0gPSAwCiAgICAgICAgICAgIHRoaXNfZm9yY2VfeWluZ2xpID0gMAogICAgICAgICAgICB0aGlzX2FsbF95aW5nbGkgPSAwCiAgICAgICAgICAgIGZvciBqeXMgaW4ganlzX2NsYXNzX2xpc3Q6CiAgICAgICAgICAgICAgICAjTG9nKGp5cy5kZWx0YV9saXN0KQogICAgICAgICAgICAgICAgX251bSArPSAxCgogICAgICAgICAgICAgICAgdGhpc19tb25leSA9IGp5cy5hY2NvdW50WydCYWxhbmNlJ10gKyBqeXMuYWNjb3VudFsnRnJvemVuQmFsYW5jZSddCiAgICAgICAgICAgICAgICB0aGlzX3N0b2NrID0ganlzLmFjY291bnRbJ1N0b2NrcyddICsganlzLmFjY291bnRbJ0Zyb3plblN0b2NrcyddIAogICAgICAgICAgICAgICAgbm93X21iWydtb25leSddICs9IHRoaXNfbW9uZXkKICAgICAgICAgICAgICAgIG5vd19tYlsnYmknXSArPSB0aGlzX3N0b2NrCiAgICAgICAgICAgICAgICBub3dfbWJbJ3pnJ10gKz0gdGhpc19tb25leSArIHRoaXNfc3RvY2sgKiBqeXMuVGlja2VyWydMYXN0J10KICAgICAgICAgICAgICAgIG5vd19tYlsncGluZ2p1bl9wcmljZSddID0gKG5vd19tYlsncGluZ2p1bl9wcmljZSddICsganlzLlRpY2tlclsnTGFzdCddKQogICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICB0aGlzX2ZvcmNlX3lpbmdsaSArPSAoIHRoaXNfbW9uZXkgLSBqeXMuZmlyc3RfQmFsYW5jZSArIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgKCB0aGlzX3N0b2NrIC0ganlzLmZpcnN0X2Ftb3VudCApICoganlzLlRpY2tlclsnTGFzdCddICkKCiAgICAgICAgICAgIG5vd19tYlsncGluZ2p1bl9wcmljZSddID0gbm93X21iWydwaW5nanVuX3ByaWNlJ10vX251bQogICAgICAgICAgICAKICAgICAgICAgICAgdGhpc19hbGxfeWluZ2xpID0gbm93X21iWyd6ZyddIC0gY2h1c2hpWyd6ZyddCiAgICAgICAgICAgIAogICAgICAgICAgICBiZ193b3JkcyA9ICAoICfliJ3lp4vlrprku7fotKfluIHkuLo6JyArIHN0ciggX04oY2h1c2hpWydtb25leSddLCBwcmljZV9OKSApICsgJyzliJ3lp4vllYblk4HluIHkuLo6JyArIHN0ciggX04oY2h1c2hpWydiaSddLCBhbW91bnRfTikgKSArIAogICAgICAgICAgICAgICAgICAgICAgICAgJyAs5Yid5aeL55qE5Lqk5piT5omA5bmz5Z2H5Lu35qC85Li677yaJyArIHN0ciggX04oIGNodXNoaVsnZmlzdF9wcmljZSddLCBwcmljZV9OKSApICsgJyAs5YeA5YC85Li6JyArIHN0ciggX04oY2h1c2hpWyd6ZyddLCBwcmljZV9OKSApICsKICAgICAgICAgICAgICAgICAgICAgICAgICAnLOeOsOWcqOWumuS7t+i0p+W4geS4uicgKyBzdHIoIF9OKG5vd19tYlsnbW9uZXknXSwgcHJpY2VfTikgKSArICcs546w5Zyo5ZWG5ZOB5biB5Li6JyArIHN0ciAoIF9OKG5vd19tYlsnYmknXSwgYW1vdW50X04pICkgKyAKICAgICAgICAgICAgICAgICAgICAgICAgICfvvIznjrDlnKjlubPlnYfluIHku7fkuLrvvJonICsgc3RyKCBfTiggbm93X21iWydwaW5nanVuX3ByaWNlJ10gLCBwcmljZV9OKSApICsgJyzlh4DlgLzkuLonICsgc3RyKCBfTihub3dfbWJbJ3pnJ10sIHByaWNlX04gKSApICsKICAgICAgICAgICAgICAgICAgICAgICAgICfvvIzlvZPliY3lpZfliKnlt67kuLonICsgc3RyKHRhb2xpX2NoYSkgKyAnJSwg5LiK5LiA5qyh5omA5pyJ5pON5L2c5oC75bu26L+f5Li677yaJyArIHN0ciggX04odGhpc190aW1lX2NoYSwgMikgKSArICfnp5InICkKICAgICAgICAgICAgCiAgICAgICAgICAgIGVuZF93b3JkcyA9ICggJ+aUtuebiueOh+S4uicgKyBzdHIoIF9OKHRoaXNfYWxsX3lpbmdsaS9jaHVzaGlbJ3pnJ10qMTAwLCAyKSApICsgJyXvvIzmkKznoJbmlLbnm4rkuLonICsgc3RyKCBfTihiYW56aHVhbl9jaGEsIHByaWNlX04pICkgKyAKICAgICAgICAgICAgICAgICAgICAgICAgICfvvIzljZXnrpfmkKznoJbmlLbnm4rnjofkuLonICsgc3RyKCBfTihiYW56aHVhbl9jaGEvY2h1c2hpWydtYyddKjEwMCAsIDIpICkgKycl77yM5b2T5YmN5Lu35qC85by65Yi25bmz5LuT77yM5LiO5Yid5aeL54q25oCB55u45q+U77yM6LaF6aKd5pS255uK5Li677yaJyArCiAgICAgICAgICAgICAgICAgICAgICAgICBzdHIoIF9OKCB0aGlzX2ZvcmNlX3lpbmdsaSAsIHByaWNlX04pICkgKyAn77yM5b2T5YmN5oC755uI5Yip5Li6JyArIHN0ciggX04oIHRoaXNfYWxsX3lpbmdsaSAsIHByaWNlX04pICkgKQogICAgICAgICAgICAKICAgICAgICAgICAgVGFibGVNYW5hZ2VyLkxvZ1N0YXR1cyggYmdfd29yZHMgLCBlbmRfd29yZHMgKQoKICAgICAgICAgICAgaWYgc2hvdWxkX3Nob3cgPiA0MDAgYW5kIGlzX3RyYWRlZF9sYXN0IDwgMSBhbmQgKCB0aGlzX2ZvcmNlX3lpbmdsaSArIGNodXNoaVsnemcnXS8xMCkgPiAoYmFuemh1YW5fY2hhICsgY2h1c2hpWyd6ZyddLzEwKSAqMC41OgogICAgICAgICAgICAgICAgc2hvdWxkX3Nob3cgPSAwCiAgICAgICAgICAgICAgICAjdGhpc19mb3JjZV95aW5nbGlfbTIgPSB0aGlzX2ZvcmNlX3lpbmdsaSowLjgKICAgICAgICAgICAgICAgIExvZ1Byb2ZpdCggdGhpc19mb3JjZV95aW5nbGkgKQogICAgICAgICAgICBlbGlmIGNpc2h1ID09MToKICAgICAgICAgICAgICAgIExvZ1Byb2ZpdCggdGhpc19mb3JjZV95aW5nbGkgKQogICAgICAgICAgICBlbHNlOgogICAgICAgICAgICAgICAgaXNfdHJhZGVkX2xhc3QgLT0gMQogICAgICAgIGV4Y2VwdDoKICAgICAgICAgICAgcGFzcwoKZGVmIG1ha2VfZGF0YV9zYXZlZCh0aGlzX3dhaXRfZm9yX3NhdmVkLCB0aGlzX2NodXNoaSwgdGhpc19qeXNfY29tcGFyZV9saXN0LCB0aGlzX2JhbnpodWFuX2NoYSk6CiAgICAKICAgIHRoaXNfd2FpdF9mb3Jfc2F2ZWRbJ3NhdmVkX2NodXNoaSddID0gdGhpc19jaHVzaGkgCiAgICB0aGlzX3dhaXRfZm9yX3NhdmVkWydzYXZlZF9iYW56aHVhbiddID0gdGhpc19iYW56aHVhbl9jaGEgCiAgICBmb3IgaSBpbiB0aGlzX2p5c19jb21wYXJlX2xpc3Q6CiAgICAgICAgI0xvZyggdGhpc193YWl0X2Zvcl9zYXZlZCApCiAgICAgICAgI0xvZyggdGhpc193YWl0X2Zvcl9zYXZlZFsnc2F2ZWRfZGVsdGEnXVtpWzBdLm5hbWVdW2lbMV0ubmFtZV0gKQogICAgICAgIAogICAgICAgICNMb2coaVsxXS5uYW1lKQogICAgICAgICNMb2codGhpc193YWl0X2Zvcl9zYXZlZFsnc2F2ZWRfZGVsdGEnXVtpWzBdLm5hbWVdW2lbMV0ubmFtZV0pCiAgICAgICAgI0xvZygnJyxpWzBdLm5hbWUsIGlbMV0ubmFtZSkKICAgICAgICAKICAgICAgICB0aGlzX3dhaXRfZm9yX3NhdmVkWydzYXZlZF9kZWx0YSddW2lbMF0ubmFtZV1baVsxXS5uYW1lXVsndHJhZGVkX3RpbWVzX2RpY3QnXSA9IGlbMF0udHJhZGVkX3RpbWVzX2RpY3RbaVsxXS5uYW1lXQogICAgICAgIHRoaXNfd2FpdF9mb3Jfc2F2ZWRbJ3NhdmVkX2RlbHRhJ11baVswXS5uYW1lXVtpWzFdLm5hbWVdWydkZWx0YV9saXN0J10gPSBpWzBdLmRlbHRhX2xpc3RbaVsxXS5uYW1lXQogICAgICAgIHRoaXNfd2FpdF9mb3Jfc2F2ZWRbJ3NhdmVkX2RlbHRhJ11baVswXS5uYW1lXVtpWzFdLm5hbWVdWydkZWx0YV9jZ19saXN0J10gPSBpWzBdLmRlbHRhX2NnX2xpc3RbaVsxXS5uYW1lXQoKICAgICAgICB0aGlzX3dhaXRfZm9yX3NhdmVkWydzYXZlZF9qeXNfZmlyc3Rfc3RhdGUnXVtpWzBdLm5hbWVdWyd0cmFkZWRfYW1vdW50J10gPSBpWzBdLnRyYWRlZF9hbW91bnQKICAgICAgICB0aGlzX3dhaXRfZm9yX3NhdmVkWydzYXZlZF9kZWx0YSddW2lbMF0ubmFtZV1baVsxXS5uYW1lXVsndHJhZGVkX3RpbWVzJ10gPSBpWzBdLnRyYWRlZF90aW1lc19kaWN0W2lbMV0ubmFtZV0KICAgIAogICAgdGhpc19zYXZlZF9uYW1lMSA9IHNhdmVkX25hbWUgKyAnMScgCiAgICB0aGlzX3NhdmVkX25hbWUyID0gc2F2ZWRfbmFtZSArICcyJwogICAgd2l0aCBvcGVuKCB0aGlzX3NhdmVkX25hbWUxLCAndycpIGFzIGY6CiAgICAgICAganNvbi5kdW1wKHRoaXNfd2FpdF9mb3Jfc2F2ZWQsIGYpCiAgICAgICAgI0xvZyggdGhpc193YWl0X2Zvcl9zYXZlZCApCiAgICAgICAgI0xvZygn5oiQ5Yqf5YKo5a2Y5paH5Lu2JykKICAgIHdpdGggb3BlbiggdGhpc19zYXZlZF9uYW1lMiwgJ3cnKSBhcyBmOgogICAgICAgIGpzb24uZHVtcCh0aGlzX3dhaXRfZm9yX3NhdmVkLCBmKQogICAgICAgICNMb2coIHRoaXNfd2FpdF9mb3Jfc2F2ZWQgKQogICAgICAgICNMb2coJ+aIkOWKn+WCqOWtmOWkh+S7veaWh+S7tuOAgjMxMScpCiAgICAgICAgCmRlZiBhZnRlcl90cmFkZV9kb19jaGVjayhqeXMpOgogICAgI+i/meS4queUqOadpeebkea1i+WPkeeUn+S6pOaYk+WQjuaYr+WQpui0puaIt+acquWPkeeUn+WPmOWMlu+8jOWmguaenOacquWPkeeUn++8jOWImei0puaIt+aOpeS4i+adpeS4jeWPguS4juS6pOaYk+OAggogICAgaWYganlzLmRvX2NoZWNrOgogICAgICAgIExvZygn5byA5aeL5qOA5rWLOicsIGp5cy5uYW1lLCAnLi4uJykKICAgICAgICBqeXMuZG9fY2hlY2sgPSBGYWxzZQogICAgICAgIHRyeToKICAgICAgICAjaWYgMToKICAgICAgICAgICAganlzLmdldF9hY2NvdW50KCkKICAgICAgICAgICAgaWYganlzLkJhbGFuY2UgPT0ganlzLmxhc3RfQmFsYW5jZSBhbmQganlzLmFtb3VudCA9PSBqeXMubGFzdF9hbW91bnQgOgogICAgICAgICAgICAgICAganlzLmVycm9yX3RpbWVzICs9IDEKICAgICAgICAgICAgICAgIGp5cy5lcnJvcl90aW1lcyA9IG1pbiggNSwganlzLmVycm9yX3RpbWVzICkgCiAgICAgICAgICAgICAgICBqeXMuZXJyb3Jfd2FpdCA9IG1lZXRfZXJyb3Jfd2FpdCoganlzLmVycm9yX3RpbWVzIAogICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICBMb2coIGp5cy5uYW1lLCAn5Zyo5Lqk5piT5pe25Ye66ZSZ77yM5o6l5LiL5p2l5a6D5pqC5pe25LiN5Y+C5LiO5Lqk5piTJywganlzLmVycm9yX3dhaXQgKQogICAgICAgICAgICAgICAgTG9nKCBqeXMuQmFsYW5jZSwnYmFsYW5jZSByaWdodCBsYXN0JywgIGp5cy5sYXN0X0JhbGFuY2UgKSAKICAgICAgICAgICAgICAgIExvZygganlzLmFtb3VudCwgJ2Ftb3VudCByaWdodCBsYXN0JywganlzLmxhc3RfYW1vdW50ICApCiAgICAgICAgICAgICAgICBMb2coICdEZWJ1Zy10aGlzOicsIGp5cy5hY2NvdW50ICkKICAgICAgICAgICAgICAgIExvZyggJ0RlYnVnLWxhc3Q6JywganlzLmxhc3RfYWNjb3VudCApCiAgICAgICAgICAgICAgICAKICAgICAgICBleGNlcHQ6CiAgICAgICAgICAgIExvZygganlzLm5hbWUsICflnKjnm5HmtYvplJnor6/kv6Hmga/ml7bvvIzojrflj5botKbmiLfkv6Hmga/lpLHotKXvvIzmraPlnKjph43or5UuLi4nKQogICAgICAgICAgICBqeXMuZXJyb3Jfd2FpdCA9IDEKICAgIApkZWYgYXV0b19jaGFuZ2VfdGFvbGljaGEobGFzdF8xMDAwX2p5X2Ftb3VudCwgbGFzdF8xMDAwX2p5X2Ftb3VudF9jaXNodSk6CiAgICBnbG9iYWwgdGFvbGlfY2hhCiAgICAj6L+Z5Liq5Ye95pWw55So5p2l5o6n5Yi26ZiI5YC86Ieq5Yqo6KGM5YqoCiAgICBpZiB0YW9saV9jaGEgPCB0YW9saV9jaGFfbWluOgogICAgICAgIHRhb2xpX2NoYSA9IHRhb2xpX2NoYV9taW4KICAgIGVsaWYgdGFvbGlfY2hhID4gdGFvbGlfY2hhX21heDoKICAgICAgICB0YW9saV9jaGEgPSB0YW9saV9jaGFfbWF4IAogICAgZWxpZiBsYXN0XzEwMDBfanlfYW1vdW50ID4gaW5pdF9hbW91bnQgKiAyNSBhbmQgbGFzdF8xMDAwX2p5X2Ftb3VudCA8IGluaXRfYW1vdW50ICogNTA6CiAgICAgICAgcmV0dXJuIGxhc3RfMTAwMF9qeV9hbW91bnQgLGxhc3RfMTAwMF9qeV9hbW91bnRfY2lzaHUKICAgIGVsc2U6CiAgICAgICAgaWYgbGFzdF8xMDAwX2p5X2Ftb3VudCA8IGluaXRfYW1vdW50IDoKICAgICAgICAgICAgdGFvbGlfY2hhIC09IDAuMDA0CiAgICAgICAgZWxpZiBsYXN0XzEwMDBfanlfYW1vdW50IDwgaW5pdF9hbW91bnQgKiAyMDoKICAgICAgICAgICAgdGFvbGlfY2hhIC09IDAuMDAxCiAgICAgICAgZWxpZiBsYXN0XzEwMDBfanlfYW1vdW50ID4gaW5pdF9hbW91bnQgKiAxMDA6CiAgICAgICAgICAgIHRhb2xpX2NoYSArPSAwLjAxNQogICAgICAgIGVsaWYgbGFzdF8xMDAwX2p5X2Ftb3VudCA+IGluaXRfYW1vdW50ICogNTA6CiAgICAgICAgICAgIHRhb2xpX2NoYSArPSAwLjAwMgogICAgICAgICAgICAKICAgICAgICBMb2coJ+ajgOa1i+WIsOWumuS9jeaXtumXtOWGheaQrOegluWNleaVsOS4ujonLGxhc3RfMTAwMF9qeV9hbW91bnQsIu+8m+WQr+WKqOmYiOWAvOabtOaWsO+8jOabtOaWsOWQjueahOmYiOWAvOS4ujoiLHRhb2xpX2NoYSkKICAgICAgICByZXR1cm4gMCwwCiAgICAKICAgIHJldHVybiBsYXN0XzEwMDBfanlfYW1vdW50ICxsYXN0XzEwMDBfanlfYW1vdW50X2Npc2h1CgpkZWYgY3JlYXRlX3RoZV90YWJsZSgganlzX2xpc3QgLCBqeXNfY29tcGFyZV9saXN0ICk6CiAgICAj6L+Z5Liq5Ye95pWw55So5p2l5Yi26YCg6KGo5Y2V5qGG5p62IAogICAganlzX251bSA9IGxlbihqeXNfbGlzdCkKICAgIGNvbF9uYW1lX2xpc3RfMSA9IFsgJ+S6pOaYk+aJgCcsJ+W9k+WJjeS5sDHku7cnLCflvZPliY3ljZYx5Lu3Jywn5L2Z6ZKxJywn5L2Z5biB5pWw6YePJywn5Y+v6LSt5Lmw5biB5pWw6YePJywn5Lqk5piT5omA5bu26L+fJywn5qih5byPJywn5Lmw5Y2W5omL57ut6LS5KCUpJywn5aWX5Yip5pWw6YePJyBdCiAgICBjb2xfbmFtZV9saXN0XzIgPSBbICfkuqTmmJPmiYDot6/lvoQnICwgJ+S4pOS6pOaYk+aJgOebruWJjeS5sOWNluS7t+agvOS/oeaBrycsJ+ivpei3r+W+hOWll+WIqeaVsOmHjycgXQogICAgCiAgICAj5Yib5bu66KGo5Y2V57G7CiAgICBUYk0gID0gQ3JlYXRlVGFibGVNYW5hZ2VyKCkKICAgIAogICAgI+a3u+WKoOWFt+S9k+eahOS4pOS4quihqOWNle+8jOWIl+mVv+S4uuWktOWQje+8jOihjOmVv+S4uuS6pOaYk+aJgO+8iOS6pOaYk+aJgOWvue+8ieS4quaVsAogICAgdGFibGVfMSA9IFRiTS5BZGRUYWJsZSgi5Lqk5piT5omA54q25oCB5L+h5oGvIiwgbGVuKGNvbF9uYW1lX2xpc3RfMSksIGp5c19udW0pIAogICAgdGFibGVfMiA9IFRiTS5BZGRUYWJsZSgi5Lqk5piT5omA5pCs56CW6Lev5b6EIiwgbGVuKGNvbF9uYW1lX2xpc3RfMiksIGxlbihqeXNfY29tcGFyZV9saXN0KSkgCiAgICAKICAgICPorr7lrprlhbfkvZPnmoTlpLTlkI3np7AKICAgIHRhYmxlXzEuU2V0Q29scyggY29sX25hbWVfbGlzdF8xICkKICAgIHRhYmxlXzIuU2V0Q29scyggY29sX25hbWVfbGlzdF8yICkKICAgIAogICAgX3RoaXNfY291bnRzID0gMAogICAgZm9yIGp5cyBpbiBqeXNfbGlzdDoKICAgICAgICBfdGhpc19jb3VudHMgKz0gMQogICAgICAgIHRhYmxlXzEuU2V0Q29sUm93KCAxLCBfdGhpc19jb3VudHMgLCBqeXMubmFtZSApCiAgICAgICAgCiAgICAgICAgCiAgICBfdGhpc19jb3VudHMgPSAwICAgIAogICAgZm9yIGp5c19jb21wYXJlIGluIGp5c19jb21wYXJlX2xpc3Q6CiAgICAgICAgX3RoaXNfY291bnRzICs9IDEKICAgICAgICBqeXNfYSA9IGp5c19jb21wYXJlWzBdLm5hbWUgCiAgICAgICAganlzX2IgPSBqeXNfY29tcGFyZVsxXS5uYW1lCiAgICAgICAgdGhpc193b3JkID0gc3RyKGp5c19hKSArICcg5ZKMICcgKyBzdHIoanlzX2IpCiAgICAgICAgdGFibGVfMi5TZXRDb2xSb3coIDEsIF90aGlzX2NvdW50cyAsIHRoaXNfd29yZCApCiAgICAgICAgCiAgICByZXR1cm4gVGJNICwgdGFibGVfMSAsIHRhYmxlXzIKICAgICAgICAKICAgIApkZWYgbWFrZV90YWJsZV93aXRoKCBUYk0gLCAgdGFibGVfMSAsIHRhYmxlXzIgLCBqeXNfbGlzdCAsIGp5c19jb21wYXJlX2xpc3QgKToKICAgICPov5nkuKrlh73mlbDnlKjmnaXmj5Dlj5bkuqTmmJPmiYDmlbDmja7mlL7lhaXlsZXnpLrnlKjooajljZUgCiAgICAKICAgIF90aGlzX2NvdW50cyA9IDAKICAgIGZvciBqeXMgaW4ganlzX2xpc3Q6CiAgICAgICAgI+i/meS4queUqOadpeWhq+WFpeS9memSse+8jOS9meW4geetieihqDHnmoTmlbDmja4KICAgICAgICBfdGhpc19jb3VudHMgKz0gMQogICAgICAgIHRhYmxlXzEuU2V0Q29sUm93KCAyICwgX3RoaXNfY291bnRzICwgX04oIGp5cy5idXlfMSAsIHByaWNlX04pICkKICAgICAgICB0YWJsZV8xLlNldENvbFJvdyggMyAsIF90aGlzX2NvdW50cyAsIF9OKCBqeXMuc2FsZV8xICwgcHJpY2VfTikgKQogICAgICAgIHRhYmxlXzEuU2V0Q29sUm93KCA0ICwgX3RoaXNfY291bnRzICwgX04oIGp5cy5CYWxhbmNlICwgcHJpY2VfTikgKQogICAgICAgIHRhYmxlXzEuU2V0Q29sUm93KCA1ICwgX3RoaXNfY291bnRzICwganlzLmFtb3VudCApCiAgICAgICAgdGFibGVfMS5TZXRDb2xSb3coIDYgLCBfdGhpc19jb3VudHMgLCBqeXMuY2FuX2J1eSApCiAgICAgICAgCiAgICAgICAgaWYganlzLnBpbmcgPT0gMDoKICAgICAgICAgICAgdGFibGVfMS5TZXRDb2xSb3coIDcgLCBfdGhpc19jb3VudHMgLCctLS0tJykKICAgICAgICBlbHNlOgogICAgICAgICAgICB0YWJsZV8xLlNldENvbFJvdyggNyAsIF90aGlzX2NvdW50cyAsIHN0ciggX04oIGp5cy5waW5nLCAxKSApICsnIG1zJykKICAgICAgICAgICAgCiAgICAgICAgdGFibGVfMS5TZXRDb2xSb3coIDggLCBfdGhpc19jb3VudHMgLCBqeXMud2Vic29ja2V0X21vZGUgKQogICAgICAgIHRhYmxlXzEuU2V0Q29sUm93KCA5ICwgX3RoaXNfY291bnRzICwgc3RyKCAn5Lmw5Y2V77yaJytzdHIoanlzLkZlZVsnQnV5J10pKyclICzljZbljZU6Jysgc3RyKGp5cy5GZWVbJ1NlbGwnXSkgKyAnJScpICkKICAgICAgICB0YWJsZV8xLlNldENvbFJvdyggMTAgLCBfdGhpc19jb3VudHMgLCBfTihqeXMudHJhZGVkX2Ftb3VudCwgYW1vdW50X04pICkKICAgICAgICAKICAgIF90aGlzX2NvdW50cyA9IDAgICAgCiAgICBmb3IganlzX2NvbXBhcmUgaW4ganlzX2NvbXBhcmVfbGlzdDoKICAgICAgICBfdGhpc19jb3VudHMgKz0gMQogICAgICAgIGp5c19hID0ganlzX2NvbXBhcmVbMF0gCiAgICAgICAganlzX2IgPSBqeXNfY29tcGFyZVsxXQogICAgICAgIAogICAgICAgIGFfYnV5MSAsIGFfc2FsZTEgPSBfTigganlzX2EuYnV5XzEgLCBwcmljZV9OICkgLCBfTigganlzX2Euc2FsZV8xICwgcHJpY2VfTiApCiAgICAgICAgYl9idXkxICwgYl9zYWxlMSA9IF9OKCBqeXNfYi5idXlfMSAsIHByaWNlX04gKSAsIF9OKCBqeXNfYi5zYWxlXzEgLCBwcmljZV9OICkKICAgICAgICAKICAgICAgICBhYnV5X2JzYWxlX2NoYSA9IGJfc2FsZTEgLSBhX2J1eTEKICAgICAgICBhc2FsZV9iYnV5X2NoYSA9IGFfc2FsZTEgLSBiX2J1eTEKICAgICAgICAKICAgICAgICB0aGlzX2RlbHRhID0ganlzX2EuZGVsdGFfbGlzdFtqeXNfYi5uYW1lXQogICAgICAgIAogICAgICAgIGRpZmZlciA9IGFicyhqeXNfYS5UaWNrZXJbJ0xhc3QnXSAtIGp5c19iLlRpY2tlclsnTGFzdCddKQogICAgICAgIGlmIGRpZmZlcj4ganViaV95dW5iaV9jaGVhY2tfYW5kX2NoYW5nZSowLjc6CiAgICAgICAgICAgIHRoaXNfbWlnaHRfa2sgPSBfTiggKGRpZmZlci9qdWJpX3l1bmJpX2NoZWFja19hbmRfY2hhbmdlICsgMSkqdGFvbGlfY2hhLCBwcmljZV9OKQogICAgICAgIGVsc2U6CiAgICAgICAgICAgIHRoaXNfbWlnaHRfa2sgPSB0YW9saV9jaGEKICAgICAgICAgICAgCiAgICAgICAgaWYgbW9yZV90aGFuX3Rhb2xpY2hhOgogICAgICAgICAgICBmZWVfYXNiYiA9IGp5c19hLkZlZVsnU2VsbCddICsganlzX2IuRmVlWydCdXknXSArIHRoaXNfbWlnaHRfa2sKICAgICAgICAgICAgZmVlX2FiYnMgPSBqeXNfYS5GZWVbJ0J1eSddICsganlzX2IuRmVlWydTZWxsJ10gKyB0aGlzX21pZ2h0X2trCiAgICAgICAgICAgIGFjaGEgPSBhX3NhbGUxIC0gYl9idXkxKiggMStmZWVfYXNiYiAqIDEuMCAvMTAwICkgLSB0aGlzX2RlbHRhIAogICAgICAgICAgICBiY2hhID0gYl9zYWxlMSAtIGFfYnV5MSooIDErZmVlX2FiYnMgKiAxLjAgLzEwMCApICsgdGhpc19kZWx0YSAgCiAgICAgICAgICAgIAogICAgICAgICAgICBpZiBiY2hhID4gMDoKICAgICAgICAgICAgICAgIHB5Y2hhID0gX04oIC0gdGhpc19kZWx0YSArIGFfYnV5MSooIGZlZV9hYmJzICogMS4wIC8xMDAgKSAsIHByaWNlX04gKQogICAgICAgICAgICAgICAgd29yZHMgPSAoIGp5c19hLm5hbWUgKyflvZPliY3kubAx5Lu35Li6JyArIHN0cihhX2J1eTEpICsgJywnICsganlzX2IubmFtZSArICcs5b2T5YmN5Y2WMeS7t+S4uicgKyBzdHIoYl9zYWxlMSkgKyAKICAgICAgICAgICAgICAgICAgICAgJ+Wkp+S6juW3ruS7tycgKyBzdHIoIHB5Y2hhICkgKyAnLOS7juS7t+agvOadpeeci+WPr+S7jicgKyBqeXNfYS5uYW1lICsgJ+S5sCcgKyBqeXNfYi5uYW1lICsgJ+WNlicgKQogICAgICAgICAgICAgICAgCiAgICAgICAgICAgIGVsaWYgYWNoYSA+IDAgOiAgICAKICAgICAgICAgICAgICAgIHB5Y2hhID0gX04oIHRoaXNfZGVsdGEgKyBiX2J1eTEgKiggZmVlX2FzYmIgKiAxLjAgLzEwMCApICwgcHJpY2VfTiApCiAgICAgICAgICAgICAgICB3b3JkcyA9ICgganlzX2EubmFtZSArJ+W9k+WJjeWNljHku7fkuLonICsgc3RyKGFfc2FsZTEpICsgJywnICsganlzX2IubmFtZSArICcs5b2T5YmN5LmwMeS7t+S4uicgKyBzdHIoYl9idXkxKSArIAogICAgICAgICAgICAgICAgICAgICAn5aSn5LqO5beu5Lu3JyArIHN0ciggcHljaGEgKSArICcs5LuO5Lu35qC85p2l55yL5Y+v5LuOJyArIGp5c19hLm5hbWUgKyAn5Y2WJyArIGp5c19iLm5hbWUgKyAn5LmwJyApCiAgICAgICAgICAgICAgICAKICAgICAgICAgICAgZWxzZToKICAgICAgICAgICAgICAgIHB5Y2hhMSA9IF9OKCAtIHRoaXNfZGVsdGEgKyBhX2J1eTEqKCBmZWVfYWJicyAqIDEuMCAvMTAwICkgLCBwcmljZV9OICkKICAgICAgICAgICAgICAgIHB5Y2hhMiA9IF9OKCB0aGlzX2RlbHRhICsgYl9idXkxICooIGZlZV9hc2JiICogMS4wIC8xMDAgKSAsIHByaWNlX04gKQogICAgICAgICAgICAgICAgd29yZHMgPSAoIGp5c19hLm5hbWUgKyflvZPliY3kubAx5Lu35Li6JyArIHN0cihhX2J1eTEpICsgJywnICsganlzX2IubmFtZSArICflvZPliY3ljZYx5Lu35Li6JyArIHN0cihiX3NhbGUxKSArICcgOyAnICsKICAgICAgICAgICAgICAgICAgICAgICAgIGp5c19hLm5hbWUgKyflvZPliY3ljZYx5Lu35Li6JyArIHN0cihhX3NhbGUxKSArICcsJyArIGp5c19iLm5hbWUgKyAn5b2T5YmN5LmwMeS7t+S4uicgKyBzdHIoYl9idXkxKSArIAogICAgICAgICAgICAgICAgICAgICAgICAgJyA7IOebruWJjeS4pOS6pOaYk+aJgOWBj+enu+W3ruS7t+WIhuWIq+S4uu+8micrICBzdHIoIHB5Y2hhMSApKyflkownICsgc3RyKCBweWNoYTIgKSArCiAgICAgICAgICAgICAgICAgICAgICAgICAnOyDnrpfkuIrlvZPliY3orr7lrprpmIjlgLzlkozmiYvnu63otLnvvIzku47ku7fmoLzmnaXnnIvml6DmiJDkuqTmnLrkvJonICkKICAgICAgICBlbHNlOiAgICAgICAgCiAgICAgICAgICAgIGlmIGFidXlfYnNhbGVfY2hhID4gLSB0aGlzX2RlbHRhICsgYV9idXkxICogdGhpc19taWdodF9rayAvIDEwMCAgOgogICAgICAgICAgICAgICAgcHljaGEgPSBfTiggKCAtdGhpc19kZWx0YSArIGFfYnV5MSAqIHRoaXNfbWlnaHRfa2sgLyAxMDApICwgcHJpY2VfTikKICAgICAgICAgICAgICAgIHdvcmRzID0gKCBqeXNfYS5uYW1lICsn5b2T5YmN5LmwMeS7t+S4uicgKyBzdHIoYV9idXkxKSArICcsJyArIGp5c19iLm5hbWUgKyAnLOW9k+WJjeWNljHku7fkuLonICsgc3RyKGJfc2FsZTEpICsgCiAgICAgICAgICAgICAgICAgICAgICAgICAn5aSn5LqO5beu5Lu3JyArIHN0ciggcHljaGEgKSArICcs5LuO5Lu35qC85p2l55yL5Y+v5LuOJyArIGp5c19hLm5hbWUgKyAn5LmwJyArIGp5c19iLm5hbWUgKyAn5Y2WJyApCiAgICAgICAgICAgICAgICAKICAgICAgICAgICAgZWxpZiBhc2FsZV9iYnV5X2NoYSA+IHRoaXNfZGVsdGEgKyBiX2J1eTEgKiB0aGlzX21pZ2h0X2trIC8gMTAwIDoKICAgICAgICAgICAgICAgIHB5Y2hhID0gX04oICggdGhpc19kZWx0YSArIGJfYnV5MSAqIHRoaXNfbWlnaHRfa2sgLyAxMDApICwgMikKICAgICAgICAgICAgICAgIHdvcmRzID0gKCBqeXNfYS5uYW1lICsn5b2T5YmN5Y2WMeS7t+S4uicgKyBzdHIoYV9zYWxlMSkgKyAnLCcgKyBqeXNfYi5uYW1lICsgJyzlvZPliY3kubAx5Lu35Li6JyArIHN0cihiX2J1eTEpICsgCiAgICAgICAgICAgICAgICAgICAgICflpKfkuo7lt67ku7cnICsgc3RyKCBweWNoYSApICsgJyzku47ku7fmoLzmnaXnnIvlj6/ku44nICsganlzX2EubmFtZSArICfljZYnICsganlzX2IubmFtZSArICfkubAnICkKICAgICAgICAgICAgZWxzZToKICAgICAgICAgICAgICAgIHB5Y2hhMSA9IF9OKCAoLXRoaXNfZGVsdGEgKyAoIGFfYnV5MSAgKSAqIHRoaXNfbWlnaHRfa2sgLyAyMDApICwgcHJpY2VfTiApCiAgICAgICAgICAgICAgICBweWNoYTIgPSBfTiggKHRoaXNfZGVsdGEgKyAoIGJfYnV5MSApICogdGhpc19taWdodF9rayAvIDIwMCkgLCBwcmljZV9OICkKICAgICAgICAgICAgICAgIHdvcmRzID0gKCBqeXNfYS5uYW1lICsn5b2T5YmN5LmwMeS7t+S4uicgKyBzdHIoYV9idXkxKSArICcsJyArIGp5c19iLm5hbWUgKyAn5b2T5YmN5Y2WMeS7t+S4uicgKyBzdHIoYl9zYWxlMSkgKyAnIDsgJyArCiAgICAgICAgICAgICAgICAgICAgICBqeXNfYS5uYW1lICsn5b2T5YmN5Y2WMeS7t+S4uicgKyBzdHIoYV9zYWxlMSkgKyAnLCcgKyBqeXNfYi5uYW1lICsgJ+W9k+WJjeS5sDHku7fkuLonICsgc3RyKGJfYnV5MSkgKyAKICAgICAgICAgICAgICAgICAgICAgJyA7IOebruWJjeS4pOS6pOaYk+aJgOWBj+enu+W3ruS7t+WIhuWIq+S4uu+8micrICBzdHIoIHB5Y2hhMSApKyflkownICsgc3RyKCBweWNoYTIgKSArCiAgICAgICAgICAgICAgICAgICAgICc7IOeul+S4iuW9k+WJjeiuvuWumumYiOWAvOWSjOaJi+e7rei0ue+8jOS7juS7t+agvOadpeeci+aXoOaIkOS6pOacuuS8micgKQogICAgICAgIAogICAgICAgIHRhYmxlXzIuU2V0Q29sUm93KCAyLCBfdGhpc19jb3VudHMgLCB3b3JkcyApCiAgICAgICAgCiAgICAgICAganlzX2FfYl90cmVhZGVkX3dvcmRzID0gX04oIGp5c19hLnRyYWRlZF90aW1lc19kaWN0W2p5c19iLm5hbWVdICwzKQogICAgICAgIHRhYmxlXzIuU2V0Q29sUm93KCAzLCBfdGhpc19jb3VudHMgLCBqeXNfYV9iX3RyZWFkZWRfd29yZHMgKQoKICAgIHJldHVybiBUYk0KCmRlZiByZV9tYWtlX2R1aWJpX2RpYyhqeXNfbGlzdCxsYXN0X2J1eSxsYXN0X3NhbGUpOgogICAgI+i/meS4quWHveaVsOeUqOadpemHjeiuvuWvueeFp+ihqAogICAgZHVpYmlfcHJpY2UgPSB7J2J1eSc6RmFsc2UsCiAgICAgICAgICAgICAgICdzYWxlJzpGYWxzZSwKICAgICAgICAgICAgICAgJ2NvdW50X3RpbWVzJzowfQogICAgCiAgICBmb3IganlzIGluIGp5c19saXN0OgogICAgICAgIHRyeToKICAgICAgICAgICAgZHVpYmlfcHJpY2VbJ2J1eSddID0gZHVpYmlfcHJpY2VbJ2J1eSddICogMC41ICsganlzLlRpY2tlclsnQnV5J10gKiAwLjUKICAgICAgICAgICAgZHVpYmlfcHJpY2VbJ3NhbGUnXSA9IGR1aWJpX3ByaWNlWydzYWxlJ10gKiAwLjUgKyBqeXMuVGlja2VyWydTZWxsJ10gKiAwLjUKICAgICAgICAgICAgCiAgICAgICAgICAgIGp5cy5kdWliaV9wcmljZVsnYnV5J10gPSBqeXMuZHVpYmlfcHJpY2VbJ2J1eSddICogMC41ICsganlzLlRpY2tlclsnQnV5J10gKiAwLjUKICAgICAgICAgICAganlzLmR1aWJpX3ByaWNlWydzYWxlJ10gPSBqeXMuZHVpYmlfcHJpY2VbJ3NhbGUnXSAqIDAuNSArIGp5cy5UaWNrZXJbJ1NlbGwnXSAqIDAuNSAKICAgICAgICAgICAgCiAgICAgICAgZXhjZXB0OgogICAgICAgICAgICBpZiBsYXN0X2J1eToKICAgICAgICAgICAgICAgIGR1aWJpX3ByaWNlWydidXknXSA9IGxhc3RfYnV5CiAgICAgICAgICAgICAgICBqeXMuZHVpYmlfcHJpY2VbJ2J1eSddID0gbGFzdF9idXkKICAgICAgICAgICAgZWxzZToKICAgICAgICAgICAgICAgIGR1aWJpX3ByaWNlWydidXknXSA9IGp5cy5UaWNrZXJbJ0J1eSddCiAgICAgICAgICAgICAgICBqeXMuZHVpYmlfcHJpY2VbJ2J1eSddID0ganlzLlRpY2tlclsnQnV5J10KICAgICAgICAgICAgICAgIAogICAgICAgICAgICBpZiBsYXN0X3NhbGU6CiAgICAgICAgICAgICAgICBkdWliaV9wcmljZVsnc2FsZSddID0gbGFzdF9zYWxlCiAgICAgICAgICAgICAgICBqeXMuZHVpYmlfcHJpY2VbJ3NhbGUnXSA9IGxhc3Rfc2FsZQogICAgICAgICAgICBlbHNlOgogICAgICAgICAgICAgICAgZHVpYmlfcHJpY2VbJ3NhbGUnXSA9IGp5cy5UaWNrZXJbJ1NlbGwnXSAqMS4xCiAgICAgICAgICAgICAgICBqeXMuZHVpYmlfcHJpY2VbJ3NhbGUnXSA9IGp5cy5UaWNrZXJbJ1NlbGwnXSAqMS4xCiAgICAgICAgICAgIGR1aWJpX3ByaWNlWydjb3VudF90aW1lcyddID0gMAogICAgICAgICAgICBqeXMuZHVpYmlfcHJpY2VbJ2NvdW50X3RpbWVzJ10gPSAwCiAgICByZXR1cm4gZHVpYmlfcHJpY2UKICAgICAgICAKZGVmIG1ha2VfdHJhZGVfZGljdChqeXNfY29tcGFyZV9saXN0KToKICAgICPov5nkuKrlh73mlbDnlKjmnaXorqHnrpflupTor6XkuqfnlJ/nmoTorqLljZUKICAgIGFsbF90cmFkZV9kaWN0ID0gW10KICAgIGZvciBpIGluIGp5c19jb21wYXJlX2xpc3Q6CiAgICAgICAgI0xvZyhpWzBdLm5hbWUpCiAgICAgICAgdHJ5OgogICAgICAgICAgICBpZiBpWzBdLnBpbmc8MjAwMCBhbmQgaVsxXS5waW5nPDIwMDA6CiAgICAgICAgICAgICAgICBvbmVfdHJhZGVfdGljID0gaVswXS5tYWtlX3RyYWRlX3dpdGhfYW1vdW50KGlbMV0gLGh1YV9kaWFuID0gaHVhZGlhbikKICAgICAgICAgICAgICAgIGlmIG9uZV90cmFkZV90aWM6CiAgICAgICAgICAgICAgICAgICAgYWxsX3RyYWRlX2RpY3QuYXBwZW5kKG9uZV90cmFkZV90aWMpCiAgICAgICAgZXhjZXB0OgogICAgICAgICAgICBpZiBpWzBdLkRlcHRoIGFuZCBpWzFdLkRlcHRoOgogICAgICAgICAgICAgICAgdHJ5OgogICAgICAgICAgICAgICAgICAgIExvZygn5Zyo5Yi25L2cJywgaVswXS5uYW1lLCAnLS0+JyxpWzFdLm5hbWUsJ+S6pOaYk+WvueaXtuWHuumUmeS6huOAgicpCiAgICAgICAgICAgICAgICAgICAgTG9nKGlbMF0ubmFtZSwgJzAuLi4nKQogICAgICAgICAgICAgICAgICAgIExvZyhpWzBdLm5hbWUsICdzdG9jazonICxpWzBdLmFjY291bnRbJ1N0b2NrcyddKQogICAgICAgICAgICAgICAgICAgIExvZyhpWzBdLm5hbWUsICdiYWxhbmNlOicsIGlbMF0uYWNjb3VudFsnQmFsYW5jZSddKQogICAgICAgICAgICAgICAgICAgIExvZyhpWzBdLm5hbWUsICdhc2tbMF06JywgaVswXS5EZXB0aFsnQXNrcyddWzBdKQogICAgICAgICAgICAgICAgICAgIExvZyhpWzBdLm5hbWUsICdhbGxfYXNrOicsIGlbMF0uRGVwdGhbJ0Fza3MnXSkKICAgICAgICAgICAgICAgICAgICBMb2coaVswXS5uYW1lLCAnYmlkc1swXScsIGlbMF0uRGVwdGhbJ0JpZHMnXVswXSkKICAgICAgICAgICAgICAgICAgICBMb2coaVswXS5uYW1lLCAnYWxsX2JpZHMnLCBpWzBdLkRlcHRoWydCaWRzJ10pCgogICAgICAgICAgICAgICAgICAgIExvZyhpWzFdLm5hbWUsICcxLi4uJykKICAgICAgICAgICAgICAgICAgICBMb2coaVsxXS5uYW1lLCAnc3RvY2s6JyAsIGlbMV0uYWNjb3VudFsnU3RvY2tzJ10pCiAgICAgICAgICAgICAgICAgICAgTG9nKGlbMV0ubmFtZSwgJ2JhbGFuY2U6JywgaVsxXS5hY2NvdW50WydCYWxhbmNlJ10pCiAgICAgICAgICAgICAgICAgICAgTG9nKGlbMV0ubmFtZSwgJ2Fza1swXTonLCBpWzFdLkRlcHRoWydBc2tzJ11bMF0pCiAgICAgICAgICAgICAgICAgICAgTG9nKGlbMV0ubmFtZSwgJ2FsbF9hc2s6JywgaVsxXS5EZXB0aFsnQXNrcyddKQogICAgICAgICAgICAgICAgICAgIExvZyhpWzFdLm5hbWUsICdiaWRzWzBdJywgaVsxXS5EZXB0aFsnQmlkcyddWzBdKQogICAgICAgICAgICAgICAgICAgIExvZyhpWzFdLm5hbWUsICdhbGxfYmlkcycsIGlbMV0uRGVwdGhbJ0JpZHMnXSkKICAgICAgICAgICAgICAgIGV4Y2VwdDoKICAgICAgICAgICAgICAgICAgICAjdHJ5OgogICAgICAgICAgICAgICAgICAgICMgICAgaWYgbm90IGlbMF0uRGVwdGg6CiAgICAgICAgICAgICAgICAgICAgIyAgICAgICAgTG9nKCfmnKrojrflj5bliLAnLGlbMF0ubmFtZSwn55qE5rex5bqmJykKICAgICAgICAgICAgICAgICAgICAjICAgIGlmIG5vdCBpWzFdLkRlcHRoOgogICAgICAgICAgICAgICAgICAgICMgICAgICAgIExvZygn5pyq6I635Y+W5YiwJyxpWzFdLm5hbWUsJ+eahOa3seW6picpCiAgICAgICAgICAgICAgICAgICAgI2V4Y2VwdDoKICAgICAgICAgICAgICAgICAgICBwYXNzCiAgICAgICAgICAgIAogICAgcmV0dXJuIGFsbF90cmFkZV9kaWN0CgpkZWYgZ2V0X2RhdGEoanlzX2xpc3QsIGp5c19jb21wYXJlX2xpc3QsIGNpc2h1ICk6CiAgICB0aGlzX2p5c25hbWUgPSBOb25lCiAgICAj5Y+q5pu05pawd2FpdF9mb3JfcmVmcmVzaOeKtuaAgeeahOS6pOaYk+aJgOeahGFjY291bnTmlbDmja7vvIzku6XpmY3kvY7lu7bov58KICAgIGZvciBpIGluIGp5c19saXN0OgogICAgICAgIGlmIGkuYWNjb3VudF9zdGF0ZSA9PSAnd2FpdF9mb3JfcmVmcmVzaCcgb3IgaS5hY2NvdW50ID09ICd3YWl0X2Zvcl9yZWZyZXNoJyBvciBjaXNodSA9PSAxIDoKICAgICAgICAgICAgI2lmIGkuYWNjb3VudF9zdGF0ZSA9PSAnd2FpdF9mb3JfcmVmcmVzaCcgOgogICAgICAgICAgICAgICAgI0xvZygn5pu05paw5LqG54q25oCB5L+h5oGv77yaJywgaS5uYW1lKQogICAgICAgICAgICAjaWYgMToKICAgICAgICAgICAgdHJ5OgogICAgICAgICAgICAgICAgdGltZV8wID0gdGltZS50aW1lKCkKICAgICAgICAgICAgICAgIHRoaXNfanlzbmFtZSA9IGkubmFtZSAKICAgICAgICAgICAgICAgIGkuZ2V0X2FjY291bnQoKQogICAgICAgICAgICAgICAgaS5hY2NvdW50X3N0YXRlID09ICdEb25lJwogICAgICAgICAgICAgICAgaS5waW5nICs9IF9OKCB0aW1lLnRpbWUoKSAtIHRpbWVfMCwgNCkqMTAwMAogICAgICAgICAgICBleGNlcHQ6CiAgICAgICAgICAgICAgICBpLmFjY291bnRfc3RhdGUgPSAnd2FpdF9mb3JfcmVmcmVzaCcgCiAgICAgICAgICAgICAgICBMb2coIHRoaXNfanlzbmFtZSwnOuiOt+WPlmFjY291bnTmlbDmja7lpLHotKUnKQogICAgICAgICAgICAgICAgCiAgICAgICAgZWxpZiAgaS5hY2NvdW50X3N0YXRlID09ICd3YWl0X2Zvcl9yZWZyZXNoX3JkJyA6CiAgICAgICAgICAgIHJkX3RpbWUgPSAxMAogICAgICAgICAgICBpZiBpLm5hbWUgaW4gWydRdW9pbmUnLCdaYWlmJywnQml0ZmluZXgnXTogCiAgICAgICAgICAgICAgICByZF90aW1lID0gMwogICAgICAgICAgICBpZiByYW5kb20ucmFuZG9tKCkqMTAwIDwgcmRfdGltZToKICAgICAgICAgICAgICAgIHRyeToKICAgICAgICAgICAgICAgICNpZiAxOgogICAgICAgICAgICAgICAgICAgIHRpbWVfMCA9IHRpbWUudGltZSgpCiAgICAgICAgICAgICAgICAgICAgaS5nZXRfYWNjb3VudCgpCiAgICAgICAgICAgICAgICAgICAgaS5hY2NvdW50X3N0YXRlID0gJ0RvbmUnCiAgICAgICAgICAgICAgICAgICAgaS5waW5nICs9IF9OKCB0aW1lLnRpbWUoKSAtIHRpbWVfMCwgNCkqMTAwMAogICAgICAgICAgICAgICAgZXhjZXB0OgogICAgICAgICAgICAgICAgICAgIExvZyggdGhpc19qeXNuYW1lLCc66ZqP5py66I635Y+WYWNjb3VudOaVsOaNruWksei0pScpCiAgICAgICAgICAgICAgICAKICAgIHRoaXNfanlzbmFtZSA9IE5vbmUKICAgIGZvciBpIGluIGp5c19saXN0OgogICAgICAgICPmjqXkuIvmnaXojrflj5Z0aWNrZXLmlbDmja4KICAgICAgICBlcnJvcl9wb3MgPSAwCiAgICAgICAgI2lmIDE6CiAgICAgICAgdHJ5OgogICAgICAgICAgICB0aW1lXzAgPSB0aW1lLnRpbWUoKSAgIAogICAgICAgICAgICB0aGlzX2p5c25hbWUgPSBpLm5hbWUKICAgICAgICAgICAgZXJyb3JfcG9zID0gMQogICAgICAgICAgICBpLmdldF90aWNrZXIoKQogICAgICAgICAgICAjZXJyb3JfcG9zID0gMgogICAgICAgICAgICAjaS5nZXRfYWNjb3VudCgpCiAgICAgICAgICAgICNlcnJvcl9wb3MgPSAzCiAgICAgICAgICAgICNpLmdldF9kZXB0aCgpCiAgICAgICAgICAgIGkucGluZyArPSBfTiggdGltZS50aW1lKCkgLSB0aW1lXzAsIDQpKjEwMDAKICAgICAgICBleGNlcHQ6CiAgICAgICAgICAgIHBhc3MKICAgICAgICAgICAgI0xvZygndGhpc19qeXNuYW1lJyx0aGlzX2p5c25hbWUsJzonLGVycm9yX3BvcykKICAgIHRyeTogICAgICAgCiAgICAgICAgZG9lc19oZV9uZWVkX2RlcHRoKGp5c19jb21wYXJlX2xpc3QpCiAgICBleGNlcHQ6CiAgICAgICAgTG9nKCfmo4DmtYvmmK/lkKbpnIDopoHojrflj5bmt7Hluqbkv6Hmga/ml7blj5HnlJ/plJnor68nKQogICAgZm9yIGkgaW4ganlzX2xpc3Q6CiAgICAj5o6l5LiL5p2l6I635Y+WZGVwdGjmlbDmja7vvJoKICAgICAgICBpZiBpLm5lZWRfZGVwdGggYW5kIGNpc2h1PiBMb29wSW50ZXJ2YWw6CiAgICAgICAgICAgICNpZiAxOgogICAgICAgICAgICB0cnk6CiAgICAgICAgICAgICAgICB0aW1lXzAgPSB0aW1lLnRpbWUoKQogICAgICAgICAgICAgICAgI0xvZygn5byA5aeL6I635Y+WJywgaS5uYW1lLCAn55qE5rex5bqm5L+h5oGvJykKICAgICAgICAgICAgICAgIGkuZ2V0X2RlcHRoKCkKICAgICAgICAgICAgICAgIGkucGluZyArPSBfTiggdGltZS50aW1lKCkgLSB0aW1lXzAsIDQpKjEwMDAKICAgICAgICAgICAgICAgIGkubmVlZF9kZXB0aCA9IEZhbHNlCiAgICAgICAgICAgIGV4Y2VwdDoKICAgICAgICAgICAgICAgIExvZyhpLm5hbWUsICfojrflj5bmt7Hluqbkv6Hmga/lh7rplJknKQogICAgICAgIAogICAgICAgIApkZWYgZG9lc19oZV9uZWVkX2RlcHRoKGp5c19jb21wYXJlX2xpc3QpOgogICAgI+eOsOWcqOWIpOaWreaYr+WQpumcgOimgeiOt+WPlua3seW6puS/oeaBrwogICAgZm9yIGkgaW4ganlzX2NvbXBhcmVfbGlzdDoKICAgICAgICBhID0gaVswXQogICAgICAgIGIgPSBpWzFdCiAgICAgICAgYVRpY2tlciA9IGEuVGlja2VyIAogICAgICAgIGJUaWNrZXIgPSBiLlRpY2tlciAKICAgICAgICBwcmljZV9hbGFzdCwgcHJpY2VfYXNlbGwsIHByaWNlX2FidXkgPSBhVGlja2VyWydMYXN0J10gLCBhVGlja2VyWydCdXknXSAsIGFUaWNrZXJbJ1NlbGwnXQogICAgICAgIHByaWNlX2JsYXN0LCBwcmljZV9ic2VsbCwgcHJpY2VfYmJ1eSA9IGJUaWNrZXJbJ0xhc3QnXSAsIGJUaWNrZXJbJ0J1eSddICwgYlRpY2tlclsnU2VsbCddCiAgICAgICAgCiAgICAgICAgZGlmZmVyID0gcHJpY2VfYWxhc3QgLSBwcmljZV9ibGFzdAogICAgICAgIGEuY2dfZGVsdGEoYi5uYW1lLGRpZmZlcikKICAgICAgICBkZWx0YSA9IGEuZGVsdGFfbGlzdFsgYi5uYW1lIF0KICAgICAgICAjTG9nKGEubmFtZSwgJy0tPicsIGIubmFtZSwgJ2RlbHRhOicsIGRlbHRhLCAnOyBkaWZmZXI6JywgZGlmZmVyICApCiAgICAgICAgaWYgZGlmZmVyPiBqdWJpX3l1bmJpX2NoZWFja19hbmRfY2hhbmdlKjAuNzoKICAgICAgICAgICAgdGhpc19taWdodF9rayA9X04oIChhYnMoZGlmZmVyKS9qdWJpX3l1bmJpX2NoZWFja19hbmRfY2hhbmdlICsgMSkqdGFvbGlfY2hhICwgcHJpY2VfTiApCiAgICAgICAgZWxzZToKICAgICAgICAgICAgdGhpc19taWdodF9rayA9IHRhb2xpX2NoYQogICAgICAgICAgICAKICAgICAgICBpZiBtb3JlX3RoYW5fdGFvbGljaGE6CiAgICAgICAgICAgIGZlZV9hc2JiID0gYS5GZWVbJ1NlbGwnXSArIGIuRmVlWydCdXknXSArIHRhb2xpX2NoYQogICAgICAgICAgICBmZWVfYWJicyA9IGEuRmVlWydCdXknXSArIGIuRmVlWydTZWxsJ10gKyB0YW9saV9jaGEKICAgICAgICAgICAgYWNoYSA9IHByaWNlX2FzZWxsIC0gcHJpY2VfYmJ1eSooIDErZmVlX2FzYmIgKiAxLjAgLzEwMCApIC0gZGVsdGEgCiAgICAgICAgICAgIGJjaGEgPSBwcmljZV9ic2VsbCAtIHByaWNlX2FidXkqKCAxK2ZlZV9hYmJzICogMS4wIC8xMDAgKSArIGRlbHRhCiAgICAgICAgZWxzZTogICAgCiAgICAgICAgICAgIGFjaGEgPSBwcmljZV9hc2VsbCAtIHByaWNlX2JidXkqKCAxK3RoaXNfbWlnaHRfa2sgKiAxLjAgLzEwMCApIC0gZGVsdGEKICAgICAgICAgICAgYmNoYSA9IHByaWNlX2JzZWxsIC0gcHJpY2VfYWJ1eSooIDErdGhpc19taWdodF9rayAqIDEuMCAvMTAwICkgKyBkZWx0YQogICAgICAgIAogICAgICAgIGlmICAgYWNoYSA+IDAgYW5kIGEuYW1vdW50ID4gQm9yRSBhbmQgYi5jYW5fYnV5ID4gQm9yRSA6CiAgICAgICAgICAgIGlbMF0ubmVlZF9kZXB0aCA9IFRydWUKICAgICAgICAgICAgaVsxXS5uZWVkX2RlcHRoID0gVHJ1ZSAKICAgICAgICBlbGlmIGJjaGEgPiAwIGFuZCBiLmFtb3VudCA+IEJvckUgYW5kIGEuY2FuX2J1eSA+IEJvckUgOgogICAgICAgICAgICBpWzBdLm5lZWRfZGVwdGggPSBUcnVlCiAgICAgICAgICAgIGlbMV0ubmVlZF9kZXB0aCA9IFRydWUgCiAgICAgICAgICAgIApkZWYgY2xlYW5fZGF0YShqeXNfbGlzdCk6CiAgICBmb3IgaSBpbiBqeXNfbGlzdDoKICAgICAgICBpLmNsZWFuQVQoKQoKZGVmIGJ1Y2FuZyhqeXNfY2xhc3NfbGlzdCAsIG5vd19tYiAsIGNodXNoaSwgbm93X2Npc2h1LCBlYXN5X3F1c2hpKToKICAgIGdsb2JhbCBkdWliaV9wcmljZSAsIHF1c2hpX2FjdGlvbl9zYXZlCiAgICAj6L+Z5Liq5Ye95pWw55So5p2l5bmz5LuT77yM5Y2z5L2/5b6X5b2T5YmN55qE5biB5pWw6YeP562J5LqO5Yid5aeL5pWw6YePCiAgICBhbGxfZmJhbGFuY2UgPSAwCiAgICBhbGxfZnN0b2NrID0gMAogICAgYnV5X2RpY3QgPSB7fQogICAgc2FsZV9kaWN0ID0ge30KICAgIGZvciBqeXMgaW4ganlzX2NsYXNzX2xpc3Q6CiAgICAgICAgdGhpc19qeXNuYW1lID0ganlzLm5hbWUKICAgICAgICB0aGlzX2NhbnNhbGVfcHJpY2UgPSBqeXMuVGlja2VyWydCdXknXQogICAgICAgIHRoaXNfY2Fuc2FsZV9hbW91bnQgPSBqeXMuYWNjb3VudFsnU3RvY2tzJ10KICAgICAgICB0aGlzX2NhbmJ1eV9wcmljZSA9IGp5cy5UaWNrZXJbJ1NlbGwnXQogICAgICAgIHRoaXNfY2FuYnV5X3N0b2NrID0ganlzLmFjY291bnRbJ0JhbGFuY2UnXSAvIHRoaXNfY2FuYnV5X3ByaWNlICowLjk5OSAKICAgICAgICBhbGxfZmJhbGFuY2UgKz0ganlzLmFjY291bnRbJ0Zyb3plbkJhbGFuY2UnXQogICAgICAgIGFsbF9mc3RvY2sgKz0ganlzLmFjY291bnRbJ0Zyb3plblN0b2NrcyddCiAgICAgICAgCiAgICAgICAgdXNlZF9zYWxlX3ByaWNlID0ganlzLmR1aWJpX3ByaWNlWydzYWxlJ10KICAgICAgICB1c2VkX2J1eV9wcmljZSA9IGp5cy5kdWliaV9wcmljZVsnYnV5J10KICAgICAgICAKICAgICAgICBzYWxlcF9saXN0ID0ge30KICAgICAgICBidXlwX2xpc3QgPSB7fQogICAgICAgIHRyeToKICAgICAgICAgICAgaWYgc2FsZXBfbGlzdFsnYW1vdW50J10gIDwgdGhpc19jYW5zYWxlX2Ftb3VudCBhbmQgdXNlZF9zYWxlX3ByaWNlIDwgdGhpc19jYW5zYWxlX3ByaWNlOgogICAgICAgICAgICAgICAgc2FsZXBfbGlzdFsncHJpY2UnXSA9IHRoaXNfY2Fuc2FsZV9wcmljZQogICAgICAgICAgICAgICAgc2FsZXBfbGlzdFsnYW1vdW50J10gPSB0aGlzX2NhbnNhbGVfYW1vdW50CiAgICAgICAgICAgICAgICBzYWxlcF9saXN0WydqeXMnXSA9IGp5cyAKICAgICAgICAgICAgICAgIHNhbGVwX2xpc3RbJ2p5c19uYW1lJ10gPSB0aGlzX2p5c25hbWUgCiAgICAgICAgICAgICAgICBzYWxlcF9saXN0Wyd1c2VkX3NhbGVfcHJpY2UnXSA9IHVzZWRfc2FsZV9wcmljZQogICAgICAgIGV4Y2VwdDoKICAgICAgICAgICAgc2FsZXBfbGlzdFsncHJpY2UnXSA9IHRoaXNfY2Fuc2FsZV9wcmljZQogICAgICAgICAgICBzYWxlcF9saXN0WydhbW91bnQnXSA9IHRoaXNfY2Fuc2FsZV9hbW91bnQKICAgICAgICAgICAgc2FsZXBfbGlzdFsnanlzJ10gPSBqeXMgCiAgICAgICAgICAgIHNhbGVwX2xpc3RbJ2p5c19uYW1lJ10gPSB0aGlzX2p5c25hbWUgICAgICAgICAKICAgICAgICAgICAgc2FsZXBfbGlzdFsndXNlZF9zYWxlX3ByaWNlJ10gPSB1c2VkX3NhbGVfcHJpY2UKICAgICAgICB0cnk6CiAgICAgICAgICAgIGlmIGJ1eXBfbGlzdFsnYW1vdW50J10gPCB0aGlzX2NhbmJ1eV9zdG9jayBhbmQgdXNlZF9idXlfcHJpY2UgPiB0aGlzX2NhbmJ1eV9wcmljZToKICAgICAgICAgICAgICAgIGJ1eXBfbGlzdFsncHJpY2UnXSA9IHRoaXNfY2FuYnV5X3ByaWNlCiAgICAgICAgICAgICAgICBidXlwX2xpc3RbJ2Ftb3VudCddID0gdGhpc19jYW5idXlfc3RvY2sKICAgICAgICAgICAgICAgIGJ1eXBfbGlzdFsnanlzJ10gPSBqeXMgCiAgICAgICAgICAgICAgICBidXlwX2xpc3RbJ2p5c19uYW1lJ10gPSB0aGlzX2p5c25hbWUgICAgCiAgICAgICAgICAgICAgICBidXlwX2xpc3RbJ3VzZWRfYnV5X3ByaWNlJ10gPSB1c2VkX2J1eV9wcmljZQogICAgICAgIGV4Y2VwdDoKICAgICAgICAgICAgYnV5cF9saXN0WydwcmljZSddID0gdGhpc19jYW5idXlfcHJpY2UKICAgICAgICAgICAgYnV5cF9saXN0WydhbW91bnQnXSA9IHRoaXNfY2FuYnV5X3N0b2NrCiAgICAgICAgICAgIGJ1eXBfbGlzdFsnanlzJ10gPSBqeXMgCiAgICAgICAgICAgIGJ1eXBfbGlzdFsnanlzX25hbWUnXSA9IHRoaXNfanlzbmFtZSAKICAgICAgICAgICAgYnV5cF9saXN0Wyd1c2VkX2J1eV9wcmljZSddID0gdXNlZF9idXlfcHJpY2UKICAgIAogICAgaWYgZWFzeV9xdXNoaToKICAgICAgICBwaW5nX2Ftb3VudCA9IG5vd19tYlsnemcnXS9ub3dfbWJbJ3BpbmdqdW5fcHJpY2UnXQogICAgICAgIHBpbmdfYW1vdW50ID0gX04oIHBpbmdfYW1vdW50LzIgLCBhbW91bnRfTiArIDEpICMg5biB6ZKx5bmz5LuT5ZCO5bqU5pyJ55qE5biBCiAgICBlbHNlOgogICAgICAgIHBpbmdfYW1vdW50ID0gY2h1c2hpWydiaSddCiAgICAgICAgCiAgICBxdXNoaV9kb19pdCA9IEZhbHNlIAogICAgaWYgcmVhbF90aW1lX2NvdW50OiAKICAgICAgICBpZiBub3dfY2lzaHUgJSAoIGR1aWJpX3RpbWVzX2NvbiAqIDMwICkgPT0gMDogCiAgICAgICAgICAgIHF1c2hpX2RvX2l0ID0gVHJ1ZSAKICAgIGVsc2U6IAogICAgICAgIGlmIGR1aWJpX3ByaWNlWydjb3VudF90aW1lcyddID4gZHVpYmlfdGltZXNfY29uOiAKICAgICAgICAgICAgcXVzaGlfZG9faXQgPSBUcnVlIAogICAgCiAgICBpZiBhbGxfZnN0b2NrIDwgMC4xICogbm93X21iWydiaSddIGFuZCBub3dfbWJbJ2JpJ10gPCAoMS4wICsgcXVzaGlfc3AgKjEuMC8xMDApICogcGluZ19hbW91bnQ6CiAgICAgICAgaWYgYnV5cF9saXN0WydwcmljZSddIDwgYnV5cF9saXN0Wyd1c2VkX2J1eV9wcmljZSddICogKCAxIC0gbGl0dGxlX2NoYW5nZSp0YW9saV9jaGEvMTAwICkgYW5kIHF1c2hpX2RvX2l0OgogICAgICAgICAgICAj5LiK5pa555qEMC45OOaOp+WItui2i+WKv+acuuS9juS6juS5i+WJjeW5s+Wdh+WUruS7t+eahOWkmuWwkeaXtui0reS5sCAKICAgICAgICAgICAgdGhpc19hbW91bnQgPSBhYnMoICggMStxdXNoaV9zcCAqMS4wLzEwMCApICogcGluZ19hbW91bnQgLSBub3dfbWJbJ2JpJ10gKSowLjYKICAgICAgICAgICAgdGhpc19hbW91bnQgPSBtaW4oIGJ1eXBfbGlzdFsnYW1vdW50J10gLHRoaXNfYW1vdW50ICkKICAgICAgICAgICAgdGhpc19hbW91bnQgPSBfTih0aGlzX2Ftb3VudCwgYW1vdW50X04pICAgICAgICAgICAgCiAgICAgICAgICAgIGlmIHRoaXNfYW1vdW50ID4gQm9yRToKICAgICAgICAgICAgICAgIGJ1eXBfbGlzdFsnanlzJ10uYnV5KCBidXlwX2xpc3RbJ3ByaWNlJ10gLCB0aGlzX2Ftb3VudCApCiAgICAgICAgICAgICAgICBMb2coJ+i2i+WKv+acuuWQr+WKqO+8jOivpeasoei0reS5sOS6hicsIHRoaXNfYW1vdW50ICwn5Y2V77yM5bmz5LuTYW1vdW50IGlzJyxwaW5nX2Ftb3VudCkKICAgICAgICAgICAgICAgICNMb2coJ+a4hembtuWJje+8micsZHVpYmlfcHJpY2UpCiAgICAgICAgICAgICAgICBkdWliaV9wcmljZSA9IHJlX21ha2VfZHVpYmlfZGljKGp5c19jbGFzc19saXN0LGJ1eXBfbGlzdFsncHJpY2UnXSxGYWxzZSkKICAgICAgICAgICAgICAgICNMb2coJ+a4hembtuWQju+8micsZHVpYmlfcHJpY2UpCiAgICAgICAgICAgICAgICBxdXNoaV9hY3Rpb25fc2F2ZS5hcHBlbmQoeydwcmljZSc6YnV5cF9saXN0WydwcmljZSddLAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAnYW1vdW50Jzp0aGlzX2Ftb3VudCwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgJ3R5cGUnOididXknfSkKICAgICAgICAgICAgCiAgICBlbGlmIGFsbF9mYmFsYW5jZSA8IDAuMSAqIG5vd19tYlsnbW9uZXknXSBhbmQgbm93X21iWydiaSddID4gKCAxLXF1c2hpX3NwICoxLjAvMTAwICkgKiBwaW5nX2Ftb3VudDoKICAgICAgICBpZiBzYWxlcF9saXN0WydwcmljZSddID4gc2FsZXBfbGlzdFsndXNlZF9zYWxlX3ByaWNlJ10gKiAoMSArIGxpdHRsZV9jaGFuZ2UqdGFvbGlfY2hhLzEwMCkgYW5kIHF1c2hpX2RvX2l0OiAgICAgICAgICAgIAogICAgICAgICAgICB0aGlzX2Ftb3VudCA9IGFicyggbm93X21iWydiaSddIC0gKCAxLXF1c2hpX3NwICoxLjAvMTAwICkgKiBwaW5nX2Ftb3VudCApKjAuNgogICAgICAgICAgICB0aGlzX2Ftb3VudCA9IG1pbiggc2FsZXBfbGlzdFsnYW1vdW50J10gLHRoaXNfYW1vdW50ICkKICAgICAgICAgICAgdGhpc19hbW91bnQgPSBfTih0aGlzX2Ftb3VudCwgYW1vdW50X04pCiAgICAgICAgICAgIGlmIHRoaXNfYW1vdW50ID4gQm9yRToKICAgICAgICAgICAgICAgIHNhbGVwX2xpc3RbJ2p5cyddLnNhbGUoIHNhbGVwX2xpc3RbJ3ByaWNlJ10sIHRoaXNfYW1vdW50ICkKICAgICAgICAgICAgICAgIExvZygn6LaL5Yq/5py65ZCv5Yqo77yM6K+l5qyh5Y2W5Ye65LqGJywgdGhpc19hbW91bnQgLCfljZXvvIzlubPku5NhbW91bnQgaXMnLCBwaW5nX2Ftb3VudCkKICAgICAgICAgICAgICAgICNMb2coJ+a4hembtuWJje+8micsZHVpYmlfcHJpY2UpCiAgICAgICAgICAgICAgICBkdWliaV9wcmljZSA9IHJlX21ha2VfZHVpYmlfZGljKGp5c19jbGFzc19saXN0LEZhbHNlLHNhbGVwX2xpc3RbJ3ByaWNlJ10pCiAgICAgICAgICAgICAgICBxdXNoaV9hY3Rpb25fc2F2ZS5hcHBlbmQoeydwcmljZSc6c2FsZXBfbGlzdFsncHJpY2UnXSwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgJ2Ftb3VudCc6dGhpc19hbW91bnQsCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICd0eXBlJzonc2FsZSd9KQogICAgICAgICAgICAgICAgI0xvZygn5riF6Zu25ZCO77yaJyxkdWliaV9wcmljZSkKICAgICAgICAKZGVmIGRlbF93aXRoX2Zyb3plbihqeXNfbGlzdCwgbm93X21iLCBlYXN5X3F1c2hpLGNodXNoaSApOgogICAgI+i/meS4quWHveaVsOeUqOadpeWkhOeQhuWGu+e7k+eahOWNleWtkCzmmI7lpKnotbfmnaXlhpnlpb0KICAgIGdsb2JhbCBiYW56aHVhbl9jaGEsIGxhc3RfYmFuemh1YW5fcHJpY2UKICAgIGJ1eV9saXN0ID0gW10KICAgIHNhbGVfbGlzdCA9IFtdCiAgICBhbGxfYnV5X2Ftb3VudCA9IDAKICAgIGFsbF9zYWxlX2Ftb3VudCA9IDAKICAgIF9kb19jaGVjayAgPSBGYWxzZQogICAgaXNfdHJhZGVkX2xhc3QgPSAwCiAgICBmb3IganlzIGluIGp5c19saXN0OgogICAgICAgIHRyeToKICAgICAgICAgICAgaWYganlzLm5hbWUgPT0gJ1phaWYnOgogICAgICAgICAgICAgICAgI+S4uuS6huWkhOeQhnphaWbnmoRub3VuY2Xpl67popjvvIzmiJHku6znrYnkuIDnp5I6IAogICAgICAgICAgICAgICAganlzLmxhc3RfdGltZV9zdGFtcCA9IG1ha2VfemFpZl9ub3VuY2VfcHJvYmxlbSgganlzLmxhc3RfdGltZV9zdGFtcCApICAgCiAgICAgICAgICAgIHRob3NlX29yZGVyID0ganlzLmV4Y2hhbmdlLkdldE9yZGVycygpCiAgICAgICAgZXhjZXB0OgogICAgICAgICAgICB0aG9zZV9vcmRlciA9IGp5cy5leGNoYW5nZS5HZXRPcmRlcnMoKQogICAgICAgIHRyeToKICAgICAgICAgICAgdGhpc19UaWNrZXIgPSBqeXMuZXhjaGFuZ2UuR2V0VGlja2VyKCkKICAgICAgICBleGNlcHQ6CiAgICAgICAgICAgIHRoaXNfVGlja2VyID0ganlzLmV4Y2hhbmdlLkdldFRpY2tlcigpICAgICAgICAgICAgCiAgICAgICAgICAgIAogICAgICAgIHRoaXNfanlzbmFtZSA9IGp5cy5uYW1lCiAgICAgICAgaWYgbGVuKHRob3NlX29yZGVyKSA+IDA6CiAgICAgICAgICAgIGlzX3RyYWRlZF9sYXN0ID0gMTAgI+agh+azqOeUseS6jui/m+ihjOS6huS6pOaYk++8jOetiTXlm57lkIjlho3ojrflj5bkv6Hmga8KICAgICAgICAgICAgZnJvemVuX2RpY3QgPSB7fQogICAgICAgICAgICBmb3Igb25lX29yZGVyIGluIHRob3NlX29yZGVyOgogICAgICAgICAgICAgICAgdGhpc19hbW91bnQgPSBfTihvbmVfb3JkZXJbJ0Ftb3VudCddIC0gb25lX29yZGVyWydEZWFsQW1vdW50J10gLCBhbW91bnRfTikKICAgICAgICAgICAgICAgIGlmIG9uZV9vcmRlclsnVHlwZSddID09IDA6CiAgICAgICAgICAgICAgICAgICAgbGFzdF9hdmdfcHJpY2UgPSBvbmVfb3JkZXJbJ1ByaWNlJ10KICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICB0cnk6CiAgICAgICAgICAgICAgICAgICAgICAgIHRoaXNfY2FuY2xlZCA9IEZhbHNlCiAgICAgICAgICAgICAgICAgICAgICAgIGlmIGp5cy5uYW1lID09ICdaYWlmJzoKICAgICAgICAgICAgICAgICAgICAgICAgICAgICPkuLrkuoblpITnkIZ6YWlm55qEbm91bmNl6Zeu6aKY77yM5oiR5Lus562J5LiA56eSOiAKICAgICAgICAgICAgICAgICAgICAgICAgICAgIGp5cy5sYXN0X3RpbWVfc3RhbXAgPSBtYWtlX3phaWZfbm91bmNlX3Byb2JsZW0oIGp5cy5sYXN0X3RpbWVfc3RhbXAgKSAgIAogICAgICAgICAgICAgICAgICAgICAgICAjdGhpc19jYW5jbGVkID0ganlzLmV4Y2hhbmdlLkNhbmNlbE9yZGVyKCBzdHIob25lX29yZGVyWydJZCddKSApCiAgICAgICAgICAgICAgICAgICAgICAgIGlmIGp5cy5uYW1lIGluIHN0cl9mcm96ZW5faWRfanlzOgogICAgICAgICAgICAgICAgICAgICAgICAgICAgdGhpc19jYW5jbGVkID0ganlzLmV4Y2hhbmdlLkNhbmNlbE9yZGVyKCBzdHIob25lX29yZGVyWydJZCddKSApCiAgICAgICAgICAgICAgICAgICAgICAgIGVsc2U6CiAgICAgICAgICAgICAgICAgICAgICAgICAgICB0aGlzX2NhbmNsZWQgPSBqeXMuZXhjaGFuZ2UuQ2FuY2VsT3JkZXIoIG9uZV9vcmRlclsnSWQnXSApCiAgICAgICAgICAgICAgICAgICAgZXhjZXB0OgogICAgICAgICAgICAgICAgICAgICAgICBMb2coJ+WHukJVR+S6hu+8jOacquiDveWPlua2iOWNle+8micsb25lX29yZGVyKQogICAgICAgICAgICAgICAgICAgICAgICBMb2coJ+ivt+ajgOafpeaYr+WQpmFwaeayoee7meWPlua2iOS6pOaYk+WNleeahOadg+mZkOOAgicsIGp5cy5uYW1lKQogICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICBpZiB0aGlzX2NhbmNsZWQ6CiAgICAgICAgICAgICAgICAgICAgICAgIGp5cy5hY2NvdW50WydCYWxhbmNlJ10gKz0ganlzLmFjY291bnRbJ0Zyb3plbkJhbGFuY2UnXQogICAgICAgICAgICAgICAgICAgICAgICBqeXMuYWNjb3VudFsnRnJvemVuQmFsYW5jZSddID0gMAogICAgICAgICAgICAgICAgICAgICAgICB0aGlzX2p5cyA9IHt9CiAgICAgICAgICAgICAgICAgICAgICAgIHRoaXNfanlzWydqeXMnXSA9IGp5cwogICAgICAgICAgICAgICAgICAgICAgICB0aGlzX2p5c1snanlzX25hbWUnXSA9IHRoaXNfanlzbmFtZQogICAgICAgICAgICAgICAgICAgICAgICB0aGlzX2p5c1sndHlwZSddID0gJ2J1eScgCiAgICAgICAgICAgICAgICAgICAgICAgIHRoaXNfanlzWydhbW91bnQnXSA9IHRoaXNfYW1vdW50CiAgICAgICAgICAgICAgICAgICAgICAgIHRoaXNfanlzWydsYXN0X3ByaWNlJ10gPSBsYXN0X2F2Z19wcmljZQogICAgICAgICAgICAgICAgICAgICAgICB0aGlzX2p5c1sncHJpY2UnXSA9IHRoaXNfVGlja2VyWydTZWxsJ10gCiAgICAgICAgICAgICAgICAgICAgICAgIGJ1eV9saXN0LmFwcGVuZCh0aGlzX2p5cykKICAgICAgICAgICAgICAgICAgICAgICAgYWxsX2J1eV9hbW91bnQgKz0gdGhpc19hbW91bnQKICAgICAgICAgICAgICAgICAgICAgICAgTG9nKCflj5bmtojkuoYnLHRoaXNfanlzbmFtZSwn55qEJyx0aGlzX2Ftb3VudCwn5Ya757uT5Lmw5Y2VLOW9k+WJjee0r+enr+S5sOWNleaVsOmHj+S4uu+8micsYWxsX2J1eV9hbW91bnQpCiAgICAgICAgICAgICAgICAgICAgICAgICNMb2coYnV5X2xpc3QpCiAgICAgICAgICAgICAgICAgICAgICAgIF9kb19jaGVjayA9IFRydWUKICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICBlbGlmIG9uZV9vcmRlclsnVHlwZSddID09IDE6CiAgICAgICAgICAgICAgICAgICAgbGFzdF9hdmdfcHJpY2UgPSBvbmVfb3JkZXJbJ1ByaWNlJ10KICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICB0cnk6CiAgICAgICAgICAgICAgICAgICAgICAgIHRoaXNfY2FuY2xlZCA9IEZhbHNlCiAgICAgICAgICAgICAgICAgICAgICAgIGlmIGp5cy5uYW1lID09ICdaYWlmJzoKICAgICAgICAgICAgICAgICAgICAgICAgICAgICPkuLrkuoblpITnkIZ6YWlm55qEbm91bmNl6Zeu6aKY77yM5oiR5Lus562J5LiA56eSOiAKICAgICAgICAgICAgICAgICAgICAgICAgICAgIGp5cy5sYXN0X3RpbWVfc3RhbXAgPSBtYWtlX3phaWZfbm91bmNlX3Byb2JsZW0oIGp5cy5sYXN0X3RpbWVfc3RhbXAgKSAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICN0aGlzX2NhbmNsZWQgPSBqeXMuZXhjaGFuZ2UuQ2FuY2VsT3JkZXIoIHN0cihvbmVfb3JkZXJbJ0lkJ10pICkKICAgICAgICAgICAgICAgICAgICAgICAgaWYganlzLm5hbWUgaW4gc3RyX2Zyb3plbl9pZF9qeXM6CiAgICAgICAgICAgICAgICAgICAgICAgICAgICB0aGlzX2NhbmNsZWQgPSBqeXMuZXhjaGFuZ2UuQ2FuY2VsT3JkZXIoIHN0cihvbmVfb3JkZXJbJ0lkJ10pICkKICAgICAgICAgICAgICAgICAgICAgICAgZWxzZToKICAgICAgICAgICAgICAgICAgICAgICAgICAgIHRoaXNfY2FuY2xlZCA9IGp5cy5leGNoYW5nZS5DYW5jZWxPcmRlciggb25lX29yZGVyWydJZCddICkKICAgICAgICAgICAgICAgICAgICBleGNlcHQ6CiAgICAgICAgICAgICAgICAgICAgICAgIExvZygn5Ye6QlVH5LqG77yM5pyq6IO95Y+W5raI5Y2V77yaJyxvbmVfb3JkZXIpCiAgICAgICAgICAgICAgICAgICAgICAgIExvZygn6K+35qOA5p+l5piv5ZCmYXBp5rKh57uZ5Y+W5raI5Lqk5piT5Y2V55qE5p2D6ZmQ44CCJywganlzLm5hbWUpCiAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgIGlmIHRoaXNfY2FuY2xlZDoKICAgICAgICAgICAgICAgICAgICAgICAganlzLmFjY291bnRbJ1N0b2NrcyddICs9IGp5cy5hY2NvdW50WydGcm96ZW5TdG9ja3MnXSAKICAgICAgICAgICAgICAgICAgICAgICAganlzLmFjY291bnRbJ0Zyb3plblN0b2NrcyddID0gMAogICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAganlzLmFjY291bnRbJ1N0b2NrcyddICs9IHRoaXNfYW1vdW50CiAgICAgICAgICAgICAgICAgICAgICAgIHRoaXNfanlzID0ge30KICAgICAgICAgICAgICAgICAgICAgICAgdGhpc19qeXNbJ2p5cyddID0ganlzCiAgICAgICAgICAgICAgICAgICAgICAgIHRoaXNfanlzWydqeXNfbmFtZSddID0gdGhpc19qeXNuYW1lCiAgICAgICAgICAgICAgICAgICAgICAgIHRoaXNfanlzWyd0eXBlJ10gPSAnc2FsZScgCiAgICAgICAgICAgICAgICAgICAgICAgIHRoaXNfanlzWydhbW91bnQnXSA9IHRoaXNfYW1vdW50CiAgICAgICAgICAgICAgICAgICAgICAgIHRoaXNfanlzWydsYXN0X3ByaWNlJ10gPSBsYXN0X2F2Z19wcmljZQogICAgICAgICAgICAgICAgICAgICAgICB0aGlzX2p5c1sncHJpY2UnXSA9IHRoaXNfVGlja2VyWydCdXknXQogICAgICAgICAgICAgICAgICAgICAgICBzYWxlX2xpc3QuYXBwZW5kKHRoaXNfanlzKQogICAgICAgICAgICAgICAgICAgICAgICBhbGxfc2FsZV9hbW91bnQgKz0gdGhpc19hbW91bnQKICAgICAgICAgICAgICAgICAgICAgICAgTG9nKCflj5bmtojkuoYnLHRoaXNfanlzbmFtZSwn55qEJyx0aGlzX2Ftb3VudCwn5Ya757uT5Y2W5Y2VLOW9k+WJjee0r+enr+WNluWNleaVsOmHj+S4uu+8micsYWxsX3NhbGVfYW1vdW50KQogICAgICAgICAgICAgICAgICAgICAgICAjTG9nKHNhbGVfbGlzdCkKICAgICAgICAgICAgICAgICAgICAgICAgX2RvX2NoZWNrID0gVHJ1ZQogICAgaWYgZWFzeV9xdXNoaTogICAgICAgICAgICAgICAgICAgIAogICAgICAgIHBpbmdfYW1vdW50ID0gbm93X21iWyd6ZyddIC8gbm93X21iWydwaW5nanVuX3ByaWNlJ10KICAgICAgICBwaW5nX2Ftb3VudCA9IF9OKCBwaW5nX2Ftb3VudCowLjUgLCBhbW91bnRfTiArMSApICMg5biB6ZKx5bmz5LuT5ZCO5bqU5pyJ55qE5biBICAgIAogICAgZWxzZToKICAgICAgICBwaW5nX2Ftb3VudCA9IGNodXNoaVsnYmknXQogICAgICAgIAogICAgaWYgYWxsX2J1eV9hbW91bnQgPiBhbGxfc2FsZV9hbW91bnQ6ICAgICAgICAKICAgICAgICB0aGlzX2Ftb3VudCA9IGFsbF9idXlfYW1vdW50IC0gYWxsX3NhbGVfYW1vdW50CiAgICAgICAgaT0wCiAgICAgICAgTG9nKCfmraPlnKjlpITnkIblhrvnu5PkubDljZUs5aSE55CG5pWw6YeP77yaJyx0aGlzX2Ftb3VudCkKICAgICAgICBub3RfZGVhbCA9IEZhbHNlCiAgICAgICAgCiAgICAgICAgaWYgbm93X21iWydiaSddIC0gdGhpc19hbW91bnQqMC42ID4gcGluZ19hbW91bnQqMC45OCA6CiAgICAgICAgICAgICNMb2coIG5vd19tYiApCiAgICAgICAgICAgIExvZyAoJ+W9k+WJjeW4geWkmuS6juW5s+W4gemSseWdh+ihoeWuueW/jeiMg+WbtOeahOW4ge+8jOaSpOmUgOWNs+WPr+S4jemcgOimgeS5sOWFpe+8jOacgOWkp+WuueW/jScsIHBpbmdfYW1vdW50KjAuOTggKyB0aGlzX2Ftb3VudCowLjYgKSAKICAgICAgICAgICAgdGhpc19hbW91bnQgPSAwIAogICAgICAgICAgICBub3RfZGVhbCA9IFRydWUKICAgICAgICBlbHNlOgogICAgICAgICAgICB3aGlsZSggdGhpc19hbW91bnQgPiBCb3JFKToKICAgICAgICAgICAgICAgIGp5cyA9IGJ1eV9saXN0W2ldWydqeXMnXQogICAgICAgICAgICAgICAganlzX2Ftb3VudCA9IGJ1eV9saXN0W2ldWydhbW91bnQnXQogICAgICAgICAgICAgICAganlzX3ByaWNlID0gYnV5X2xpc3RbaV1bJ3ByaWNlJ10KICAgICAgICAgICAgICAgIGp5c19sYXN0X3ByaWNlID0gYnV5X2xpc3RbaV1bJ2xhc3RfcHJpY2UnXQogICAgICAgICAgICAgICAganlfdHlwZSA9IGJ1eV9saXN0W2ldWyd0eXBlJ10KICAgICAgICAgICAgICAgIGp5c19uYW1lID0gYnV5X2xpc3RbaV1bJ2p5c19uYW1lJ10KICAgICAgICAgICAgICAgIHh1eWltaWFvKGp5c19uYW1lKQogICAgICAgICAgICAgICAgdGhpc19hbW91bnQgPSBqeXNfZmNob25nZnVidXkoIGp5cywganlzX2Ftb3VudCwgdGhpc19hbW91bnQsIGp5c19wcmljZSwganlfdHlwZSApCiAgICAgICAgICAgICAgICBpKz0xCiAgICAgICAgICAgICAgICAKICAgICAgICBsYXN0X2JhbnpodWFuX2NoYSA9IGJhbnpodWFuX2NoYSAqIDEuMAogICAgICAgIAogICAgICAgIGZvcl9taW51cyA9IGxhc3RfYmFuemh1YW5fcHJpY2UqMC41KiggYWxsX2J1eV9hbW91bnQgLSBhbGxfc2FsZV9hbW91bnQgKS8oIGFsbF9idXlfYW1vdW50ICkKICAgICAgICAKICAgICAgICBpZiBub3Qgbm90X2RlYWw6IAogICAgICAgICAgICBpX2RpZiA9IGFicygoIGp5c19sYXN0X3ByaWNlIC0ganlzX3ByaWNlICkvanlzX3ByaWNlKSoxMDAKICAgICAgICAgICAgaV9kaWYgPSBpX2RpZiAvIGp5cy5kaWZmX21pZ2h0X2sKICAgICAgICAgICAgZm9yX21pbnVzID0gbWluKCBmb3JfbWludXMgKiBpX2RpZiwgbGFzdF9iYW56aHVhbl9wcmljZSowLjUgKQogICAgICAgICAgICAKICAgICAgICBiYW56aHVhbl9jaGEgPSBiYW56aHVhbl9jaGEgLSBmb3JfbWludXMKICAgICAgICBpZiBsYXN0X2JhbnpodWFuX3ByaWNlIT0gMCA6CiAgICAgICAgICAgIExvZygn55Sx5LqO5pyq5a6M5YWo5oiQ5Lqk77yM5omj6Zmk6YOo5YiG5pCs56CW5pS255uKLi4uJyxfTihsYXN0X2JhbnpodWFuX2NoYSwgcHJpY2VfTiksJy0tLS0+JyxfTihiYW56aHVhbl9jaGEsIHByaWNlX04pICkKICAgICAgICAgICAgbGFzdF9iYW56aHVhbl9wcmljZSA9IDAKICAgICAgICAKICAgIGVsaWYgYWxsX2J1eV9hbW91bnQgPCBhbGxfc2FsZV9hbW91bnQgOgogICAgICAgIHRoaXNfYW1vdW50ID0gKGFsbF9zYWxlX2Ftb3VudCAtIGFsbF9idXlfYW1vdW50KQogICAgICAgIGk9MAogICAgICAgIExvZygn5q2j5Zyo5aSE55CG5Ya757uT5Y2W5Y2VLOWkhOeQhuaVsOmHj++8micsdGhpc19hbW91bnQpCiAgICAgICAgbm90X2RlYWwgPSBGYWxzZQogICAgICAgIGlmIG5vd19tYlsnYmknXSArIHRoaXNfYW1vdW50KiAwLjYgPCBwaW5nX2Ftb3VudCoxLjAyIDoKICAgICAgICAgICAgI0xvZyggbm93X21iICkKICAgICAgICAgICAgTG9nICgn5b2T5YmN5biB5bCP5LqO5bmz5biB6ZKx5Z2H6KGh5a655b+N6IyD5Zu05YaF55qE5biB77yM5pKk6ZSA5Y2z5Y+v5LiN6ZyA6KaB5Y2W5Ye677yM5pyA5aSn5a655b+NJyxwaW5nX2Ftb3VudCoxLjAyIC0gdGhpc19hbW91bnQqIDAuNikKICAgICAgICAgICAgdGhpc19hbW91bnQgPSAwCiAgICAgICAgICAgIG5vdF9kZWFsID0gVHJ1ZQogICAgICAgIGVsc2U6CiAgICAgICAgICAgIHdoaWxlKCB0aGlzX2Ftb3VudCA+IEJvckUpOgogICAgICAgICAgICAgICAganlzID0gc2FsZV9saXN0W2ldWydqeXMnXQogICAgICAgICAgICAgICAganlzX2Ftb3VudCA9IHNhbGVfbGlzdFtpXVsnYW1vdW50J10KICAgICAgICAgICAgICAgIGp5c19sYXN0X3ByaWNlID0gc2FsZV9saXN0W2ldWydsYXN0X3ByaWNlJ10KICAgICAgICAgICAgICAgIGp5c19wcmljZSA9IHNhbGVfbGlzdFtpXVsncHJpY2UnXQogICAgICAgICAgICAgICAganlfdHlwZSA9IHNhbGVfbGlzdFtpXVsndHlwZSddCiAgICAgICAgICAgICAgICBqeXNfbmFtZSA9IHNhbGVfbGlzdFtpXVsnanlzX25hbWUnXQogICAgICAgICAgICAgICAgeHV5aW1pYW8oanlzX25hbWUpCiAgICAgICAgICAgICAgICB0aGlzX2Ftb3VudCA9IGp5c19mY2hvbmdmdWJ1eSgganlzLCBqeXNfYW1vdW50LCB0aGlzX2Ftb3VudCwganlzX3ByaWNlLCBqeV90eXBlICkKICAgICAgICAgICAgICAgIGkrPTEKICAgICAgICAgICAgICAgIAogICAgICAgIGxhc3RfYmFuemh1YW5fY2hhID0gYmFuemh1YW5fY2hhICAqIDEuMAogICAgICAgIAogICAgICAgIGZvcl9taW51cyA9IGxhc3RfYmFuemh1YW5fcHJpY2UqMC41KihhbGxfc2FsZV9hbW91bnQgLSBhbGxfYnV5X2Ftb3VudCkvKCBhbGxfc2FsZV9hbW91bnQpCiAgICAgICAgaWYgbm90IG5vdF9kZWFsOiAKICAgICAgICAgICAgaV9kaWYgPSBhYnMoKCBqeXNfbGFzdF9wcmljZSAtIGp5c19wcmljZSApL2p5c19wcmljZSkqMTAwCiAgICAgICAgICAgIGlfZGlmID0gaV9kaWYgLyBqeXMuZGlmZl9taWdodF9rCiAgICAgICAgICAgIGZvcl9taW51cyA9IG1pbiggZm9yX21pbnVzICogaV9kaWYsIGxhc3RfYmFuemh1YW5fcHJpY2UqMC41ICkKICAgICAgICAgICAgCiAgICAgICAgYmFuemh1YW5fY2hhID0gYmFuemh1YW5fY2hhIC0gZm9yX21pbnVzCiAgICAgICAgaWYgbGFzdF9iYW56aHVhbl9wcmljZSE9IDAgOgogICAgICAgICAgICBsYXN0X2JhbnpodWFuX3ByaWNlID0gMAogICAgICAgICAgICBMb2coJ+eUseS6juacquWujOWFqOaIkOS6pO+8jOaJo+mZpOmDqOWIhuaQrOegluaUtuebii4uLicsX04obGFzdF9iYW56aHVhbl9jaGEsIHByaWNlX04pLCctLS0tPicsX04oYmFuemh1YW5fY2hhLCBwcmljZV9OKSApCiAgICAgICAgICAgIAogICAgICAgIAogICAgZWxpZiBfZG9fY2hlY2s6CiAgICAgICAgTG9nKCflhrvnu5PkubDljZXmlbDph4/kuLo6JyxhbGxfYnV5X2Ftb3VudCwn5Ya757uT5Y2W5Y2V5pWw6YeP5Li6JyxhbGxfc2FsZV9hbW91bnQsJ+WGu+e7k+eahOS5sOWNleWNluWNleaVsOmHj+ebuOWQjO+8jOebtOaOpeWPlua2iOWNs+WPr+OAgicpCiAgICAgICAgbGFzdF9iYW56aHVhbl9jaGEgPSBiYW56aHVhbl9jaGEgICogMS4wCiAgICAgICAgYmFuemh1YW5fY2hhID0gYmFuemh1YW5fY2hhIC0gbGFzdF9iYW56aHVhbl9wcmljZQogICAgICAgIExvZygn55Sx5LqO5pyq5a6M5YWo5oiQ5Lqk77yM5omj6Zmk6YOo5YiG5pCs56CW5pS255uKLi4uJyxfTihsYXN0X2JhbnpodWFuX2NoYSwgcHJpY2VfTiksJy0tLS0+JyxfTihiYW56aHVhbl9jaGEsIHByaWNlX04pICkKICAgICAgICBsYXN0X2JhbnpodWFuX3ByaWNlID0gMAogICAgICAgIAogICAgZm9yIGp5cyBpbiBqeXNfbGlzdDoKICAgICAgICAjanlzLmFjY291bnRfc3RhdGUgPSAnd2FpdF9mb3JfcmVmcmVzaCcKICAgICAgICBqeXMuZG9fY2hlY2sgPSBGYWxzZQogICAgIAogICAgcmV0dXJuIGlzX3RyYWRlZF9sYXN0CgoKZGVmIGp5c19mY2hvbmdmdWJ1eSgganlzLCBqeXNfYW1vdW50LCB0aGlzX2Ftb3VudCwganlzX3ByaWNlLCBqeV90eXBlICk6CiAgICBkZWFsZWQgPSBGYWxzZQogICAgaWYganlzX2Ftb3VudCA8IHRoaXNfYW1vdW50OgogICAgICAgIGlmIGp5X3R5cGUgPT0gJ2J1eSc6CiAgICAgICAgICAgIGRlYWxlZCA9IGp5cy5idXkoIGp5c19wcmljZSArIGh1YWRpYW4gLGp5c19hbW91bnQpCiAgICAgICAgZWxpZiBqeV90eXBlID09ICdzYWxlJzoKICAgICAgICAgICAgZGVhbGVkID0ganlzLnNhbGUoIGp5c19wcmljZSAtIGh1YWRpYW4gLGp5c19hbW91bnQpCiAgICAgICAgZWxzZToKICAgICAgICAgICAgTG9nKCfkuqTmmJPmiYDorqLljZXkv6Hmga/lh7rnjrDplJnor6/vvIxkZmItMzMxJykKICAgICAgICBMb2coJ+S9mWFtb3VudCDkuLrvvJonLHRoaXNfYW1vdW50LWp5c19hbW91bnQpCiAgICAgICAgaWYgZGVhbGVkOgogICAgICAgICAgICByZXR1cm4gdGhpc19hbW91bnQtanlzX2Ftb3VudAogICAgICAgIGVsc2U6CiAgICAgICAgICAgIHJldHVybiB0aGlzX2Ftb3VudAogICAgZWxzZToKICAgICAgICBpZiBqeV90eXBlID09ICdidXknOgogICAgICAgICAgICBkZWFsZWQgPSBqeXMuYnV5KCBqeXNfcHJpY2UgKyBodWFkaWFuLCB0aGlzX2Ftb3VudCkKICAgICAgICBlbGlmIGp5X3R5cGUgPT0gJ3NhbGUnOgogICAgICAgICAgICBkZWFsZWQgPSBqeXMuc2FsZSgganlzX3ByaWNlIC0gaHVhZGlhbiAsdGhpc19hbW91bnQpCiAgICAgICAgZWxzZToKICAgICAgICAgICAgTG9nKCfkuqTmmJPmiYDorqLljZXkv6Hmga/lh7rnjrDplJnor6/vvIxkZmItMzMxJykKICAgICAgICBpZiBkZWFsZWQgOgogICAgICAgICAgICByZXR1cm4gMCAgICAgICAgCiAgICAgICAgZWxzZToKICAgICAgICAgICAgcmV0dXJuIHRoaXNfYW1vdW50CiAgICAgICAgCmRlZiB4dXlpbWlhbyhqeXNfbmFtZSk6CiAgICBpZiBqeXNfbmFtZSAgPT0gJ0JUQ1RyYWRlJzoKICAgICAgICBTbGVlcCgxMDAwKQogICAgICAgICAgICAgICAgICAgIApkZWYgbGV0X3VzX3RyYWRlKHRyYWRlX2RpY3QpOgogICAgI+i/meS4quWHveaVsOeUqOadpeS6pOaYkwogICAgZ2xvYmFsIGJhbnpodWFuX2NoYSwgbGFzdF9iYW56aHVhbl9wcmljZQogICAgc2FsZV9qeXMgPSB0cmFkZV9kaWN0WydzYWxlX2p5cyddCiAgICBidXlfanlzID0gdHJhZGVfZGljdFsnYnV5X2p5cyddCiAgICAKICAgIGJ1eV9wcmljZSA9IHRyYWRlX2RpY3RbJ2J1eV9wcmljZSddCiAgICBzYWxlX3ByaWNlID0gdHJhZGVfZGljdFsnc2FsZXNfcHJpY2UnXQoKICAgIE9hbW91bnQgPSB0cmFkZV9kaWN0WydPYW1vdW50J10KICAgIHl1emhpID0gQm9yRSAKICAgIAogICAgaWYgT2Ftb3VudCA+IHRyYWRlX2RpY3RbJ3Nob3VsZF9sZXNzX3RoYW4nXToKICAgICAgICBPYW1vdW50ID0gdHJhZGVfZGljdFsnc2hvdWxkX2xlc3NfdGhhbiddCiAgICAgICAgCiAgICBpZiAgT2Ftb3VudCA+PSB5dXpoaSA6CiAgICAgICAgI0xvZygnT2Ftb3VudCcsT2Ftb3VudCwneXV6aGknLHl1emhpKQogICAgICAgIHRyeToKICAgICAgICAgICAgdGhpc19idXlfaWQgPSBidXlfanlzLmJ1eSggYnV5X3ByaWNlICwgT2Ftb3VudCApCiAgICAgICAgZXhjZXB0OgogICAgICAgICAgICBidXlfanlzLmVycm9yX3RpbWVzICs9IDEKICAgICAgICAgICAgYnV5X2p5cy5lcnJvcl90aW1lcyA9IG1pbiggNSwgYnV5X2p5cy5lcnJvcl90aW1lcyApCiAgICAgICAgICAgIGJ1eV9qeXMuZXJyb3Jfd2FpdCA9IG1lZXRfZXJyb3Jfd2FpdCogYnV5X2p5cy5lcnJvcl90aW1lcwogICAgICAgICAgICBMb2coIGJ1eV9qeXMubmFtZSwgJ+WHuumUmeS6hu+8jOaOpeS4i+adpeWug+aaguaXtuS4jeWPguS4juS6pOaYkycpCiAgICAgICAgICAgIAogICAgICAgIGR1aWJpX3ByaWNlWydidXknXSA9IGR1aWJpX3ByaWNlWydidXknXSAqIDAuOCArIGJ1eV9wcmljZSAqIDAuMgogICAgICAgIGJ1eV9qeXMudHJhZGVkX2Ftb3VudCArPSBPYW1vdW50IAogICAgICAgIHRyeToKICAgICAgICAgICAgdGhpc19zYWxlX2lkID0gc2FsZV9qeXMuc2FsZSggc2FsZV9wcmljZSAsIE9hbW91bnQgKQogICAgICAgIGV4Y2VwdDoKICAgICAgICAgICAgc2FsZV9qeXMuZXJyb3JfdGltZXMgKz0gMQogICAgICAgICAgICBzYWxlX2p5cy5lcnJvcl90aW1lcyA9IG1pbiggNSwgc2FsZV9qeXMuZXJyb3JfdGltZXMgKSAKICAgICAgICAgICAgc2FsZV9qeXMuZXJyb3Jfd2FpdCA9IG1lZXRfZXJyb3Jfd2FpdCogd2FpdF9jb3VudAogICAgICAgICAgICBMb2coIHNhbGVfanlzLm5hbWUsICflh7rplJnkuobvvIzmjqXkuIvmnaXlroPmmoLml7bkuI3lj4LkuI7kuqTmmJMnKQogICAgICAgICAgICAKICAgICAgICBkdWliaV9wcmljZVsnc2FsZSddID0gZHVpYmlfcHJpY2VbJ3NhbGUnXSAqIDAuOCArIHNhbGVfcHJpY2UgKiAwLjIKICAgICAgICBzYWxlX2p5cy50cmFkZWRfYW1vdW50ICs9IE9hbW91bnQgCiAgICAgICAgCiAgICAgICAgaWYgdHJhZGVfZGljdFsnd2F5J10gPT0gJ2EyYic6CiAgICAgICAgICAgIHNhbGVfanlzLnRyYWRlZF90aW1lc19kaWN0W2J1eV9qeXMubmFtZV0gKz0gT2Ftb3VudCAKICAgICAgICBlbGlmIHRyYWRlX2RpY3RbJ3dheSddID09ICdiMmEnOgogICAgICAgICAgICBidXlfanlzLnRyYWRlZF90aW1lc19kaWN0W3NhbGVfanlzLm5hbWVdICs9IE9hbW91bnQgCiAgICAgICAgZWxzZToKICAgICAgICAgICAgTG9nKCd0cmFkZV9kaWN0OicsdHJhZGVfZGljdCkKICAgICAgICBkdWliaV9wcmljZVsnY291bnRfdGltZXMnXSArPSBPYW1vdW50ICogMzAKICAgICAgICAKICAgICAgICBpZiByZWFsX2NvdW50X2ZlZToKICAgICAgICAgICAgdGhpc19mZWUgPSAoIHNhbGVfcHJpY2Uqc2FsZV9qeXMuRmVlWydTZWxsJ10gKyBidXlfcHJpY2UqYnV5X2p5cy5GZWVbJ0J1eSddICkqT2Ftb3VudC8xMDAKICAgICAgICAgICAgbGFzdF9iYW56aHVhbl9wcmljZSA9IChzYWxlX3ByaWNlIC0gYnV5X3ByaWNlICkqT2Ftb3VudCAtIHRoaXNfZmVlCiAgICAgICAgZWxzZToKICAgICAgICAgICAgbGFzdF9iYW56aHVhbl9wcmljZSA9IChzYWxlX3ByaWNlIC0gYnV5X3ByaWNlICkqT2Ftb3VudCAqICggdGFvbGlfY2hhIC0gc2FsZV9qeXMuRmVlWydTZWxsJ10gLSBidXlfanlzLkZlZVsnQnV5J10gKS90YW9saV9jaGEKICAgICAgICAgICAgCiAgICAgICAgYmFuemh1YW5fY2hhICs9IGxhc3RfYmFuemh1YW5fcHJpY2UgCiAgICAKICAgIHJldHVybiBPYW1vdW50ICAgICAgCiAgICAgICAgI0xvZ1N0YXR1cygn5LulJyxidXlfcHJpY2UsJ+eahOS7t+agvOS7jicsYnV5X2p5cy5uYW1lICwn5Lmw5YWl77yM5LulJyxzYWxlX3ByaWNlLCfnmoTku7fmoLzku44nLHNhbGVfanlzLm5hbWUgLCfljZblh7onLE9hbW91bnQpCiAgICAgICAgCmRlZiBtYWtlX2NvbXBhcmVfZGljdChleGNoYW5nZXMpOgogICAgI+i/meS4quWHveaVsOeUqOadpeaKimV4Y2hhbmdlc+mHjOeahOaJgOaciemFjeWvuemFjeWHuuadpSzov5Tlm55kaWN0CiAgICBqeXNfY29tcGFyZV9saXN0ID0gW10KICAgIG0gPSBsZW4oZXhjaGFuZ2VzKS0xCiAgICBmb3IgaSBpbiByYW5nZShtKToKICAgICAgICBmb3IgaiBpbiByYW5nZShtLWkpOgogICAgICAgICAgICAjTG9nKGksaitpKzEsZXhjaGFuZ2VzW2ldLm5hbWUsZXhjaGFuZ2VzW2oraSsxXS5uYW1lKQogICAgICAgICAgICAjanlzX2NvbXBhcmVfbGlzdC5hcHBlbmQoIChleGNoYW5nZXNbaV0ubmFtZSxleGNoYW5nZXNbaitpKzFdLm5hbWUpICkKICAgICAgICAgICAganlzX2NvbXBhcmVfbGlzdC5hcHBlbmQoIChleGNoYW5nZXNbaV0sZXhjaGFuZ2VzW2oraSsxXSkgKQogICAgcmV0dXJuIGp5c19jb21wYXJlX2xpc3QgCgpjbGFzcyBKWVM6CiAgICBkZWYgX19pbml0X18oc2VsZix0aGlzX2V4Y2hhbmdlICk6CiAgICAgICAgI+WIneWni+WMlgogICAgICAgIHNlbGYuZXhjaGFuZ2UgPSB0aGlzX2V4Y2hhbmdlCiAgICAgICAgc2VsZi5sYXN0X3RpbWVfc3RhbXAgPSB0aW1lLnRpbWUoKQogICAgICAgIHRyeToKICAgICAgICAgICAgc2VsZi5uYW1lID0gc2VsZi5leGNoYW5nZS5HZXROYW1lICgpCiAgICAgICAgZXhjZXB0OgogICAgICAgICAgICBzZWxmLm5hbWUgPSBzZWxmLmV4Y2hhbmdlLkdldE5hbWUgKCkKICAgICAgICAgICAgCiAgICAgICAgdHJ5OgogICAgICAgICAgICBMb2coJ0EnLCBzZWxmLm5hbWUsJ3R5cGU6JywgdHlwZShzZWxmLm5hbWUpKQogICAgICAgICAgICBzZWxmLm5hbWUgPSBzZWxmLm5hbWUuZGVjb2RlKGVuY29kaW5nPSJ1dGYtOCIpCiAgICAgICAgZXhjZXB0OgogICAgICAgICAgICBMb2coJ0InLCBzZWxmLm5hbWUsICd0eXBlOiBzdHInICkKICAgICAgICAgICAgc2VsZi5uYW1lID0gc3RyKCBzZWxmLm5hbWUgKQogICAgICAgIHNlbGYubmFtZSA9IHN0ciggc2VsZi5uYW1lICkKICAgICAgICAKICAgICAgICB0cnk6CiAgICAgICAgICAgIHNlbGYuVGlja2VyID0gIHNlbGYuZXhjaGFuZ2UuR2V0VGlja2VyICgpCiAgICAgICAgZXhjZXB0OgogICAgICAgICAgICBzZWxmLlRpY2tlciA9ICBzZWxmLmV4Y2hhbmdlLkdldFRpY2tlciAoKQogICAgICAgICAgICAKICAgICAgICB0cnk6CiAgICAgICAgICAgIHNlbGYuYWNjb3VudCA9IHNlbGYuZXhjaGFuZ2UuR2V0QWNjb3VudCAoKQogICAgICAgIGV4Y2VwdDoKICAgICAgICAgICAgc2VsZi5hY2NvdW50ID0gc2VsZi5leGNoYW5nZS5HZXRBY2NvdW50ICgpCiAgICAgICAgICAgIAogICAgICAgIHRyeToKICAgICAgICAgICAgc2VsZi5EZXB0aCA9IHNlbGYuZXhjaGFuZ2UuR2V0RGVwdGggKCkKICAgICAgICBleGNlcHQ6CiAgICAgICAgICAgIHNlbGYuRGVwdGggPSBzZWxmLmV4Y2hhbmdlLkdldERlcHRoICgpCiAgICAgICAgICAgIAogICAgICAgIHRyeToKICAgICAgICAgICAgc2VsZi5GZWUgPSBGRUVfRElDX09USEVSW3NlbGYubmFtZV0KICAgICAgICBleGNlcHQ6CiAgICAgICAgICAgIHNlbGYuRmVlID0gRkVFX0RJQwogICAgICAgIHNlbGYuYWNjb3VudF9zdGF0ZSA9ICd3YWl0X2Zvcl9yZWZyZXNoJwogICAgICAgIHNlbGYuZmlyc3RfQmFsYW5jZSA9IHNlbGYuYWNjb3VudFsnQmFsYW5jZSddIAogICAgICAgIHNlbGYuZmlyc3RfYW1vdW50ID0gc2VsZi5hY2NvdW50WydTdG9ja3MnXQogICAgICAgIHNlbGYuZmlyc3RfcHJpY2UgPSBzZWxmLlRpY2tlclsnTGFzdCddCiAgICAgICAgc2VsZi5idXlfMSA9IHNlbGYuVGlja2VyWydTZWxsJ10KICAgICAgICBzZWxmLnNhbGVfMSA9IHNlbGYuVGlja2VyWydCdXknXSAKICAgICAgICAKICAgICAgICBzZWxmLmRvX2NoZWNrID0gRmFsc2UKICAgICAgICBzZWxmLm5lZWRfZGVwdGggPSBGYWxzZQogICAgICAgIHNlbGYubGFzdF9CYWxhbmNlID0gJy0tLS0nCiAgICAgICAgc2VsZi5sYXN0X2Ftb3VudCA9ICctLS0tJwogICAgICAgIHNlbGYubGFzdF9hY2NvdW50ID0gJy0tLS0nCiAgICAgICAgCiAgICAgICAgc2VsZi53ZWJzb2NrZXRfbW9kZSA9IE5vbmUKICAgICAgICBzZWxmLnBpbmcgPSBOb25lIAogICAgICAgIHNlbGYudHJhZGVkX3RpbWVzX2RpY3QgPSB7fQogICAgICAgIHNlbGYuZGVsdGFfbGlzdCA9IHt9CiAgICAgICAgc2VsZi5kZWx0YV9jZ19saXN0ID0ge30KICAgICAgICBzZWxmLnRyYWRlZF9hbW91bnQgPSAwCiAgICAgICAgc2VsZi5lcnJvcl90aW1lcyA9IDAKICAgICAgICBzZWxmLmVycm9yX3dhaXQgPSAwCiAgICAgICAgc2VsZi5kdWliaV9wcmljZSA9IHsnYnV5JzpGYWxzZSwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICdzYWxlJzpGYWxzZSwKICAgICAgICAgICAgICAgICAgICAgICAgICAgICdjb3VudF90aW1lcyc6MH0KICAgICAgICAKICAgIGRlZiBnZXRfdGlja2VyKHNlbGYpOgogICAgICAgICPojrflj5bluILlnLrooYzmg4UKICAgICAgICBpZiBzZWxmLm5hbWUgPT0gJ1phaWYnOgogICAgICAgICAgICAj5Li65LqG5aSE55CGemFpZueahG5vdW5jZemXrumimO+8jOaIkeS7rOetieS4gOenkjogCiAgICAgICAgICAgIHNlbGYubGFzdF90aW1lX3N0YW1wID0gbWFrZV96YWlmX25vdW5jZV9wcm9ibGVtKCBzZWxmLmxhc3RfdGltZV9zdGFtcCApCiAgICAgICAgdGhpc19UaWNrZXIgPSBzZWxmLmV4Y2hhbmdlLkdldFRpY2tlcigpCiAgICAgICAgaWYgcmFuZG9tLnJhbmRvbSgpICogMTAwIDw1MDoKICAgICAgICAgICAgaWYgc2VsZi5idXlfMSowLjggPiB0aGlzX1RpY2tlclsnU2VsbCddOgogICAgICAgICAgICAgICAgTG9nKCfkubDkuIDku7fkuKXph43kvY7kuo7kuIrkuIDmrKHvvIzkvLDorqHmnI3liqHlmajlj4jlh7rpl67popjkuobvvJonLHNlbGYubmFtZSkKICAgICAgICAgICAgICAgIExvZyh0aGlzX1RpY2tlcikKICAgICAgICAgICAgICAgIExvZyhzZWxmLlRpY2tlcikKICAgICAgICAgICAgZWxpZiBzZWxmLmJ1eV8xKjEuMyA8IHRoaXNfVGlja2VyWydCdXknXToKICAgICAgICAgICAgICAgIExvZygn5Lmw5LiA5Lu35Lil6YeN6auY5LqO5LiK5LiA5qyh77yM5Lyw6K6h5pyN5Yqh5Zmo5Y+I5Ye66Zeu6aKY5LqG77yaJyxzZWxmLm5hbWUpCiAgICAgICAgICAgICAgICBMb2codGhpc19UaWNrZXIpCiAgICAgICAgICAgICAgICBMb2coc2VsZi5UaWNrZXIpICAgIAogICAgICAgICAgICBlbGlmIHNlbGYuc2FsZV8xKjEuMSA8IHRoaXNfVGlja2VyWydCdXknXToKICAgICAgICAgICAgICAgIExvZygn5Y2W5LiA5Lu35Lil6YeN6auY5LqO5LiK5LiA5qyh77yM5Lyw6K6h5pyN5Yqh5Zmo5Y+I5Ye66Zeu6aKY5LqG77yaJyxzZWxmLm5hbWUpCiAgICAgICAgICAgICAgICBMb2codGhpc19UaWNrZXIpCiAgICAgICAgICAgICAgICBMb2coc2VsZi5UaWNrZXIpCiAgICAgICAgICAgIGVsaWYgc2VsZi5zYWxlXzEqMC43ID4gdGhpc19UaWNrZXJbJ0J1eSddOgogICAgICAgICAgICAgICAgTG9nKCfljZbkuIDku7fkuKXph43kvY7kuo7kuIrkuIDmrKHvvIzkvLDorqHmnI3liqHlmajlj4jlh7rpl67popjkuobvvJrvvJonLHNlbGYubmFtZSkKICAgICAgICAgICAgICAgIExvZyh0aGlzX1RpY2tlcikKICAgICAgICAgICAgICAgIExvZyhzZWxmLlRpY2tlcikKICAgICAgICAgICAgZWxzZTogICAgCiAgICAgICAgICAgICAgICAjTG9nKCd0aGlzJyx0aGlzX1RpY2tlcikKICAgICAgICAgICAgICAgICNMb2coJ2xhc3QnLHNlbGYuVGlja2VyKQogICAgICAgICAgICAgICAgc2VsZi5UaWNrZXIgPSB0aGlzX1RpY2tlcgogICAgICAgICAgICAgICAgc2VsZi5idXlfMSA9IHRoaXNfVGlja2VyWydTZWxsJ10KICAgICAgICAgICAgICAgIHNlbGYuc2FsZV8xID0gdGhpc19UaWNrZXJbJ0J1eSddCiAgICAgICAgZWxzZToKICAgICAgICAgICAgc2VsZi5UaWNrZXIgPSB0aGlzX1RpY2tlcgogICAgICAgICAgICBzZWxmLmJ1eV8xID0gdGhpc19UaWNrZXJbJ1NlbGwnXQogICAgICAgICAgICBzZWxmLnNhbGVfMSA9IHRoaXNfVGlja2VyWydCdXknXQoKICAgIGRlZiBnZXRfYWNjb3VudChzZWxmKToKICAgICAgICAj6I635Y+W6LSm5oi35L+h5oGvCiAgICAgICAgaWYgc2VsZi5uYW1lID09ICdaYWlmJzoKICAgICAgICAgICAgI+S4uuS6huWkhOeQhnphaWbnmoRub3VuY2Xpl67popjvvIzmiJHku6znrYnkuIDnp5I6IAogICAgICAgICAgICBzZWxmLmxhc3RfdGltZV9zdGFtcCA9IG1ha2VfemFpZl9ub3VuY2VfcHJvYmxlbSggc2VsZi5sYXN0X3RpbWVfc3RhbXAgKQogICAgICAgICAgICAKICAgICAgICBzZWxmLmVycm9yX3BvcyA9IDAKICAgICAgICBzZWxmLkJhbGFuY2UgPSAn5pyq6I635Y+W5Yiw5pWw5o2uJwogICAgICAgIHNlbGYuYW1vdW50ID0gJ+acquiOt+WPluWIsOaVsOaNricKICAgICAgICBzZWxmLmNhbl9idXkgPSAn5pyq6I635Y+W5Yiw5pWw5o2uJwogICAgICAgIHNlbGYuRnJvemVuQmFsYW5jZSA9ICfmnKrojrflj5bliLDmlbDmja4nCiAgICAgICAgc2VsZi5Gcm96ZW5TdG9ja3MgPSAn5pyq6I635Y+W5Yiw5pWw5o2uJwogICAgICAgIHNlbGYuZXJyb3JfcG9zID0gMQogICAgICAgIAogICAgICAgIHNlbGYuYWNjb3VudCA9IHNlbGYuZXhjaGFuZ2UuR2V0QWNjb3VudCgpCiAgICAgICAgc2VsZi5lcnJvcl9wb3MgPSAyCiAgICAgICAgc2VsZi5lcnJvcl90aGluZyA9IHNlbGYuYWNjb3VudAoKICAgICAgICBzZWxmLkJhbGFuY2UgPSBfTiggc2VsZi5hY2NvdW50WydCYWxhbmNlJ10gLCBwcmljZV9OICkKICAgICAgICBzZWxmLmFtb3VudCA9IF9OKCBzZWxmLmFjY291bnRbJ1N0b2NrcyddICwgYW1vdW50X04gKQogICAgICAgIHNlbGYuRnJvemVuQmFsYW5jZSA9IF9OKCBzZWxmLmFjY291bnRbJ0Zyb3plbkJhbGFuY2UnXSAsIHByaWNlX04gKQogICAgICAgIHNlbGYuRnJvemVuU3RvY2tzID0gX04oIHNlbGYuYWNjb3VudFsnRnJvemVuU3RvY2tzJ10gLCBhbW91bnRfTiApCiAgICAgICAgc2VsZi5jYW5fYnV5ID0gX04oICggc2VsZi5CYWxhbmNlICAvIHNlbGYuc2FsZV8xICkgLCBhbW91bnRfTiApCiAgICAgICAgCiAgICAgICAgc2VsZi5hY2NvdW50X3N0YXRlID0gJ0RvbmUnCiAgICAgICAgCiAgICAgICAgc2VsZi5lcnJvcl9wb3MgPSAzCiAgICAgICAgCiAgICBkZWYgZ2V0X2RlcHRoKHNlbGYpOgogICAgICAgICPojrflj5bmt7Hluqbkv6Hmga8KICAgICAgICBpZiBzZWxmLm5hbWUgPT0gJ1phaWYnOgogICAgICAgICAgICAj5Li65LqG5aSE55CGemFpZueahG5vdW5jZemXrumimO+8jOaIkeS7rOetieS4gOenkjogCiAgICAgICAgICAgIHNlbGYubGFzdF90aW1lX3N0YW1wID0gbWFrZV96YWlmX25vdW5jZV9wcm9ibGVtKCBzZWxmLmxhc3RfdGltZV9zdGFtcCApCiAgICAgICAgc2VsZi5EZXB0aCA9IHNlbGYuZXhjaGFuZ2UuR2V0RGVwdGgoKQogICAgICAgIAogICAgZGVmIGNsZWFuQVQoc2VsZik6CiAgICAgICAgI+a4heepuui0puaIt+S/oeaBr+WSjOW4guWcuuihjOaDheS/oeaBrwogICAgICAgICNzZWxmLmFjY291bnQgPSBOb25lCiAgICAgICAgI3NlbGYuVGlja2VyID0gTm9uZSAKICAgICAgICBzZWxmLkRlcHRoID0gTm9uZSAKICAgICAgICBzZWxmLnBpbmcgPSAwCiAgICAgICAgCiAgICBkZWYgZGVsdGFfaW5pdChzZWxmLCBqeXNfYiAsaW5pdF9kZWx0YSApOgogICAgICAgICPliJ3lp4vljJblgY/nva7ph48KICAgICAgICAKICAgICAgICBkaWZmZXIgPSBhYnMoc2VsZi5UaWNrZXJbJ0xhc3QnXSAtIGp5c19iLlRpY2tlclsnTGFzdCddKQogICAgICAgIAogICAgICAgIGlmIGRpZmZlciA8IDAuMyoganViaV95dW5iaV9jaGVhY2tfYW5kX2NoYW5nZSA6CiAgICAgICAgICAgIGRlbHRhX2RlbHRhX2NnMSA9IDAuMipkZWx0YV9kZWx0YV9VMQogICAgICAgIGVsaWYgZGlmZmVyIDwgMC43ICoganViaV95dW5iaV9jaGVhY2tfYW5kX2NoYW5nZSA6CiAgICAgICAgICAgIGRlbHRhX2RlbHRhX2NnMSA9IDAuNSpkZWx0YV9kZWx0YV9VMQogICAgICAgIGVsc2U6CiAgICAgICAgICAgIGRlbHRhX2RlbHRhX2NnMSA9IGRlbHRhX2RlbHRhX1UxCiAgICAgICAgCiAgICAgICAgc2VsZi50cmFkZWRfdGltZXNfZGljdFtqeXNfYi5uYW1lXSA9IDAKICAgICAgICBzZWxmLmRlbHRhX2xpc3RbanlzX2IubmFtZV0gPSAoc2VsZi5UaWNrZXJbJ0xhc3QnXSAtIGp5c19iLlRpY2tlclsnTGFzdCddKSpkZWx0YV9kZWx0YV9jZzEqMC4wMQogICAgICAgIHNlbGYuZGVsdGFfY2dfbGlzdFtqeXNfYi5uYW1lXSA9IHsgJ3RpbWVzJzowLAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgJ2RpZmZlcl9sZWlqaSc6MH0KICAgIAogICAgZGVmIGNnX2RlbHRhKHNlbGYsYl9uYW1lLGRpZmZlcik6CiAgICAgICAgI0xvZyhzZWxmLmRlbHRhX2NnX2xpc3QpCiAgICAgICAgI0xvZygnMS50aW1lcyBpcycsIHNlbGYuZGVsdGFfY2dfbGlzdFtiX25hbWVdWyd0aW1lcyddLCcgdGhpc19kZWx0YSBpcycgLCBzZWxmLmRlbHRhX2xpc3RbYl9uYW1lXSkKICAgICAgICAKICAgICAgICBzZWxmLmRlbHRhX2NnX2xpc3RbYl9uYW1lXVsnZGlmZmVyX2xlaWppJ10gKz0gZGlmZmVyCiAgICAgICAgc2VsZi5kZWx0YV9jZ19saXN0W2JfbmFtZV1bJ3RpbWVzJ10gKz0gMQogICAgICAgIAogICAgICAgIGlmIHNlbGYuZGVsdGFfY2dfbGlzdFtiX25hbWVdWyd0aW1lcyddID4gMjA6CiAgICAgICAgICAgIGlmIGNnX2RlbHRhX3NwZWVkID09IDE6CiAgICAgICAgICAgICAgICBsYXN0X2NnID0gMC45OTk4CiAgICAgICAgICAgICAgICB0aGlzX2NnID0gMC4wMDAxOQogICAgICAgICAgICBlbGlmIGNnX2RlbHRhX3NwZWVkID09IDI6CiAgICAgICAgICAgICAgICBsYXN0X2NnID0gMC45OTk1CiAgICAgICAgICAgICAgICB0aGlzX2NnID0gMC4wMDA0OCAgICAgICAgICAKICAgICAgICAgICAgZWxpZiBjZ19kZWx0YV9zcGVlZCA9PSAzOgogICAgICAgICAgICAgICAgbGFzdF9jZyA9IDAuOTk4CiAgICAgICAgICAgICAgICB0aGlzX2NnID0gMC4wMDE4CiAgICAgICAgICAgIGVsaWYgY2dfZGVsdGFfc3BlZWQgPT0gNDoKICAgICAgICAgICAgICAgIGxhc3RfY2cgPSAwLjk5NwogICAgICAgICAgICAgICAgdGhpc19jZyA9IDAuMDAyOCAgICAgICAgICAgIAogICAgICAgICAgICAKICAgICAgICAgICAgdGhpc19jZ19kaWZmZXIgPSBzZWxmLmRlbHRhX2NnX2xpc3RbYl9uYW1lXVsnZGlmZmVyX2xlaWppJ10vMjAKICAgICAgICAgICAgc2VsZi5kZWx0YV9saXN0W2JfbmFtZV0gPSBzZWxmLmRlbHRhX2xpc3RbYl9uYW1lXSpsYXN0X2NnICsgdGhpc19jZ19kaWZmZXIgKiB0aGlzX2NnCiAgICAgICAgICAgIHNlbGYuZGVsdGFfY2dfbGlzdFtiX25hbWVdWyd0aW1lcyddID0gMAogICAgICAgICAgICBzZWxmLmRlbHRhX2NnX2xpc3RbYl9uYW1lXVsnZGlmZmVyX2xlaWppJ10gPSAwCiAgICAgICAgI0xvZygnMi50aW1lcyBpcycsIHNlbGYuZGVsdGFfY2dfbGlzdFtiX25hbWVdWyd0aW1lcyddLCcgdGhpc19kZWx0YSBpcycgLCBzZWxmLmRlbHRhX2xpc3RbYl9uYW1lXSkKICAgICAgICAKICAgIGRlZiBidXkoc2VsZiwgcHJpY2UsYW1vdW50ICk6CiAgICAgICAgI+aMieeFp3ByaWNl5b6X5Lu35qC85ZKMYW1vdW5055qE5Lu35qC85Lmw5LiA5Y2VCiAgICAgICAgaWYgYW1vdW50IDwgQm9yRToKICAgICAgICAgICAgTG9nKCfov5nkuIDljZXlsI/kuo7kuoblj6/kuqTmmJPnmoTmnIDlsI/ljZXvvIzmn5DkuKrkuqTmmJPmiYDlj6/og73kuI3mjqXlj5cnLHNlbGYubmFtZSxhbW91bnQpCiAgICAgICAgZWxzZToKICAgICAgICAgICAgc2VsZi5kb19jaGVjayA9IFRydWUKICAgICAgICAgICAgc2VsZi5sYXN0X0JhbGFuY2UgPSBzZWxmLkJhbGFuY2UKICAgICAgICAgICAgc2VsZi5sYXN0X2FjY291bnQgPSBzZWxmLmFjY291bnQKICAgICAgICAgICAgCiAgICAgICAgICAgIHByaWNlID0gX04ocHJpY2UsIHByaWNlX04pCiAgICAgICAgICAgIGFtb3VudCA9IF9OKGFtb3VudCwgYW1vdW50X04pCiAgICAgICAgICAgIHNlbGYuYWNjb3VudF9zdGF0ZSA9ICd3YWl0X2Zvcl9yZWZyZXNoJwogICAgICAgICAgICAjc2VsZi5hY2NvdW50ID0gJ3dhaXRfZm9yX3JlZnJlc2gnCiAgICAgICAgICAgICPkuIvpnaLkuKTooYzmmK/osIPor5XnlKjnmoTvvIzmraPlvI/niYjorrDlvpfliKDpmaQKICAgICAgICAgICAgI2lmIGZvcl90ZXN0ID4yMDAwIGFuZCBmb3JfdGVzdCA8IDYwMDA6CiAgICAgICAgICAgICMgICAgTG9nKCflvIDlp4vosIPor5XplJnor6/kv6Hmga/vvJonKQogICAgICAgICAgICAjICAgIHJldHVybiAKICAgICAgICAgICAgCiAgICAgICAgICAgIGlmIHNlbGYubmFtZSA9PSAnWmFpZic6CiAgICAgICAgICAgICAgICAj5Li65LqG5aSE55CGemFpZueahG5vdW5jZemXrumimO+8jOaIkeS7rOetieS4gOenkjogCiAgICAgICAgICAgICAgICBzZWxmLmxhc3RfdGltZV9zdGFtcCA9IG1ha2VfemFpZl9ub3VuY2VfcHJvYmxlbSggc2VsZi5sYXN0X3RpbWVfc3RhbXAgKQogICAgICAgICAgICAgICAgCiAgICAgICAgICAgIHJldHVybl9idXkgPSBzZWxmLmV4Y2hhbmdlLkJ1eSggcHJpY2UsYW1vdW50ICkKICAgICAgICAgICAgaWYgc2VsZi5uYW1lID09ICdaYWlmJzoKICAgICAgICAgICAgICAgICPkuLTml7bop6PlhrPmlrnmoYgKICAgICAgICAgICAgICAgIHNlbGYubGFzdF90aW1lX3N0YW1wID0gbWFrZV96YWlmX25vdW5jZV9wcm9ibGVtKCBzZWxmLmxhc3RfdGltZV9zdGFtcCApIAogICAgICAgICAgICAgICAgCiAgICAgICAgICAgIHJldHVybiggcmV0dXJuX2J1eSApCiAgICAgICAgCiAgICBkZWYgc2FsZShzZWxmLCBwcmljZSxhbW91bnQgKToKICAgICAgICAj5oyJ54WncHJpY2Xlvpfku7fmoLzlkoxhbW91bnTnmoTku7fmoLzljZbkuIDljZUKICAgICAgICBpZiBhbW91bnQgPCBCb3JFOgogICAgICAgICAgICBMb2coJ+i/meS4gOWNleWwj+S6juS6huWPr+S6pOaYk+eahOacgOWwj+WNle+8jOafkOS4quS6pOaYk+aJgOWPr+iDveS4jeaOpeWPlycsc2VsZi5uYW1lLGFtb3VudCkKICAgICAgICBlbHNlOgogICAgICAgICAgICBzZWxmLmRvX2NoZWNrID0gVHJ1ZQogICAgICAgICAgICBzZWxmLmxhc3RfYW1vdW50ID0gc2VsZi5hbW91bnQKICAgICAgICAgICAgc2VsZi5sYXN0X2FjY291bnQgPSBzZWxmLmFjY291bnQKICAgICAgICAgICAgCiAgICAgICAgICAgIHByaWNlID0gX04ocHJpY2UsIHByaWNlX04pIAogICAgICAgICAgICBhbW91bnQgPSBfTihhbW91bnQsIGFtb3VudF9OKSAKICAgICAgICAgICAgc2VsZi5hY2NvdW50X3N0YXRlID0gJ3dhaXRfZm9yX3JlZnJlc2gnCiAgICAgICAgICAgICNzZWxmLmFjY291bnQgPSAnd2FpdF9mb3JfcmVmcmVzaCcKICAgICAgICAgICAgCiAgICAgICAgICAgIGlmIHNlbGYubmFtZSA9PSAnWmFpZic6CiAgICAgICAgICAgICAgICAj5Li65LqG5aSE55CGemFpZueahG5vdW5jZemXrumimO+8jOaIkeS7rOetieS4gOenkjogCiAgICAgICAgICAgICAgICBzZWxmLmxhc3RfdGltZV9zdGFtcCA9IG1ha2VfemFpZl9ub3VuY2VfcHJvYmxlbSggc2VsZi5sYXN0X3RpbWVfc3RhbXAgKSAgCiAgICAgICAgICAgICAgICAKICAgICAgICAgICAgcmV0dXJuX3NhbGUgPSBzZWxmLmV4Y2hhbmdlLlNlbGwoIHByaWNlLGFtb3VudCApCiAgICAgICAgICAgIGlmIHNlbGYubmFtZSA9PSAnWmFpZic6CiAgICAgICAgICAgICAgICAj5Li05pe26Kej5Yaz5pa55qGICiAgICAgICAgICAgICAgICBzZWxmLmxhc3RfdGltZV9zdGFtcCA9IG1ha2VfemFpZl9ub3VuY2VfcHJvYmxlbSggc2VsZi5sYXN0X3RpbWVfc3RhbXAgKSAKICAgICAgICAgICAgICAgIAogICAgICAgICAgICByZXR1cm4gKCByZXR1cm5fc2FsZSApCiAgICAgICAgCiAgICBkZWYgbWFrZV90cmFkZV90byhzZWxmLGp5c19iLGh1YV9kaWFuID0gMC4xKToKICAgICAgICAj6K6h566X5pys5Lqk5piT5omA55u45a+55LqOYuS6pOaYk+aJgOW6lOivpeS5sOi/mOaYr+WNlu+8jOS7peWPiuivpeiuvuWumueahOS7t+agvOOAggogICAgICAgIGEgPSBzZWxmIAogICAgICAgIGIgPSBqeXNfYgogICAgICAgIGFUaWNrZXIgPSBzZWxmLlRpY2tlciAKICAgICAgICBiVGlja2VyID0ganlzX2IuVGlja2VyIAogICAgICAgIGFfbmFtZSA9IHNlbGYubmFtZSAKICAgICAgICBiX25hbWUgPSBqeXNfYi5uYW1lIAogICAgICAgIGFfZGVwdGggPSBzZWxmLkRlcHRoCiAgICAgICAgYl9kZXB0aCA9IGp5c19iLkRlcHRoCiAgICAgICAgCiAgICAgICAgcHJpY2VfYWxhc3QsIHByaWNlX2FzZWxsLCBwcmljZV9hYnV5ID0gYVRpY2tlclsnTGFzdCddICwgYVRpY2tlclsnQnV5J10gLCBhVGlja2VyWydTZWxsJ10KICAgICAgICBwcmljZV9ibGFzdCwgcHJpY2VfYnNlbGwsIHByaWNlX2JidXkgPSBiVGlja2VyWydMYXN0J10gLCBiVGlja2VyWydCdXknXSAsIGJUaWNrZXJbJ1NlbGwnXQogICAgICAgIAogICAgICAgIGRlcHRoX2FidXlfYW0sZGVwdGhfYXNlbGxfYW0gPSBhX2RlcHRoWydBc2tzJ11bMF1bJ0Ftb3VudCddICwgYV9kZXB0aFsnQmlkcyddWzBdWydBbW91bnQnXQogICAgICAgIGRlcHRoX2JidXlfYW0sZGVwdGhfYnNlbGxfYW0gPSBiX2RlcHRoWydBc2tzJ11bMF1bJ0Ftb3VudCddICwgYl9kZXB0aFsnQmlkcyddWzBdWydBbW91bnQnXQogICAgICAgIAogICAgICAgICNMb2coJ2FtIGEgYnV5IGFuZCBzZWxsIGlzJywgZGVwdGhfYWJ1eV9hbSxkZXB0aF9hc2VsbF9hbSAsJ2IgYnV5IGFuZCBzZWxsIGlzJywgZGVwdGhfYmJ1eV9hbSAsIGRlcHRoX2JzZWxsX2FtICkKICAgICAgICAKICAgICAgICBwcmljZV9hc2VsbCxwcmljZV9ic2VsbCA9IHByaWNlX2FzZWxsIC1odWFfZGlhbiAscHJpY2VfYnNlbGwtaHVhX2RpYW4KICAgICAgICBwcmljZV9hYnV5LHByaWNlX2JidXkgPSBwcmljZV9hYnV5ICtodWFfZGlhbiAsIHByaWNlX2JidXkgK2h1YV9kaWFuCiAgICAgICAgCiAgICAgICAgCiAgICAgICAgZGlmZmVyID0gcHJpY2VfYWxhc3QgLSBwcmljZV9ibGFzdAogICAgICAgIHNlbGYuY2dfZGVsdGEoYl9uYW1lLGRpZmZlcikKICAgICAgICBkZWx0YSA9IHNlbGYuZGVsdGFfbGlzdFtiX25hbWVdCiAgICAgICAgb3V0cHV0ID0ge30KICAgICAgICBpZiBkaWZmZXI+IGp1YmlfeXVuYmlfY2hlYWNrX2FuZF9jaGFuZ2UqMC43OgogICAgICAgICAgICB0aGlzX21pZ2h0X2trID1fTiggKGFicyhkaWZmZXIpL2p1YmlfeXVuYmlfY2hlYWNrX2FuZF9jaGFuZ2UgKyAxKSp0YW9saV9jaGEgLDIgKQogICAgICAgIGVsc2U6CiAgICAgICAgICAgIHRoaXNfbWlnaHRfa2sgPSB0YW9saV9jaGEKICAgICAgICAgICAgCiAgICAgICAgaWYgbW9yZV90aGFuX3Rhb2xpY2hhOgogICAgICAgICAgICAKICAgICAgICAgICAgZmVlX2FzYmIgPSBhLkZlZVsnU2VsbCddICsgYi5GZWVbJ0J1eSddICsgdGhpc19taWdodF9rawogICAgICAgICAgICBmZWVfYWJicyA9IGEuRmVlWydCdXknXSArIGIuRmVlWydTZWxsJ10gKyB0aGlzX21pZ2h0X2trCgogICAgICAgICAgICBhY2hhID0gcHJpY2VfYXNlbGwgLSBwcmljZV9iYnV5KiggMStmZWVfYXNiYiAqIDEuMCAvMTAwICkgLSBkZWx0YSAKICAgICAgICAgICAgYmNoYSA9IHByaWNlX2JzZWxsIC0gcHJpY2VfYWJ1eSooIDErZmVlX2FiYnMgKiAxLjAgLzEwMCApICsgZGVsdGEKICAgICAgICAgICAgCiAgICAgICAgZWxzZTogICAgCiAgICAgICAgICAgIGFjaGEgPSBwcmljZV9hc2VsbCAtIHByaWNlX2JidXkqKCAxK3RoaXNfbWlnaHRfa2sgKiAxLjAgLzEwMCApIC0gZGVsdGEKICAgICAgICAgICAgYmNoYSA9IHByaWNlX2JzZWxsIC0gcHJpY2VfYWJ1eSooIDErdGhpc19taWdodF9rayAqIDEuMCAvMTAwICkgKyBkZWx0YQogICAgICAgIAogICAgICAgIHRoaXNfbWlnaHRfa2sgPSBtYXgoIHRoaXNfbWlnaHRfa2ssdGFvbGlfY2hhICkKICAgICAgICBzZWxmLmRpZmZfbWlnaHRfayA9IHRoaXNfbWlnaHRfa2sKICAgICAgICBqeXNfYi5kaWZmX21pZ2h0X2sgPSB0aGlzX21pZ2h0X2trCiAgICAgICAgCiAgICAgICAgaWYgYWNoYSA+IDAgOgogICAgICAgICAgICBvdXRwdXRbJ3NhbGVfanlzJ10gPSBhCiAgICAgICAgICAgIG91dHB1dFsnc2FsZV9qeXNfbmFtZSddID0gYV9uYW1lCiAgICAgICAgICAgIG91dHB1dFsnc2FsZXNfcHJpY2UnXSA9IHByaWNlX2FzZWxsCiAgICAgICAgICAgIG91dHB1dFsnYnV5X2p5cyddID0gYgogICAgICAgICAgICBvdXRwdXRbJ2J1eV9qeXNfbmFtZSddID0gYl9uYW1lCiAgICAgICAgICAgIG91dHB1dFsnYnV5X3ByaWNlJ10gPSBwcmljZV9iYnV5CiAgICAgICAgICAgIG91dHB1dFsnZGVsdGEnXSA9IGRlbHRhCiAgICAgICAgICAgIG91dHB1dFsnamlhY2hhJ10gPSBhY2hhCiAgICAgICAgICAgIG91dHB1dFsnb21sJ10gPSBtaW4oZGVwdGhfYXNlbGxfYW0sZGVwdGhfYmJ1eV9hbSkgCiAgICAgICAgICAgIG91dHB1dFsnd2F5J10gPSAnYTJiJwogICAgICAgICAgICAjTG9nKCdkZXB0aF9hc2VsbCxidXk6JyxkZXB0aF9hc2VsbF9hbSxkZXB0aF9iYnV5X2FtKQoKICAgICAgICBlbGlmIGJjaGEgPiAwIDoKICAgICAgICAgICAgb3V0cHV0WydzYWxlX2p5cyddID0gYgogICAgICAgICAgICBvdXRwdXRbJ3NhbGVfanlzX25hbWUnXSA9IGJfbmFtZQogICAgICAgICAgICBvdXRwdXRbJ3NhbGVzX3ByaWNlJ10gPSBwcmljZV9ic2VsbAogICAgICAgICAgICBvdXRwdXRbJ2J1eV9qeXMnXSA9IGEKICAgICAgICAgICAgb3V0cHV0WydidXlfanlzX25hbWUnXSA9IGFfbmFtZQogICAgICAgICAgICBvdXRwdXRbJ2J1eV9wcmljZSddID0gcHJpY2VfYWJ1eQogICAgICAgICAgICBvdXRwdXRbJ2RlbHRhJ10gPSBkZWx0YQogICAgICAgICAgICBvdXRwdXRbJ2ppYWNoYSddID0gYmNoYQogICAgICAgICAgICBvdXRwdXRbJ29tbCddID0gbWluKGRlcHRoX2JzZWxsX2FtLGRlcHRoX2FidXlfYW0pIAogICAgICAgICAgICBvdXRwdXRbJ3dheSddID0gJ2IyYScKICAgICAgICAgICAgI0xvZygnZGVwdGhfYnNlbGwsYnV5OicsZGVwdGhfYnNlbGxfYW0sZGVwdGhfYWJ1eV9hbSkKICAgICAgICAgICAgCiAgICAgICAgZWxzZToKICAgICAgICAgICAgb3V0cHV0ID0gTm9uZQogICAgICAgICAgICAKICAgICAgICAjTG9nKGFfbmFtZSxhY2hhLGJfbmFtZSxiY2hhKQogICAgICAgICNpZiBvdXRwdXQ6CiAgICAgICAgICAgICNMb2coYV9uYW1lLGJfbmFtZSxkZWx0YSkKICAgICAgICAgICAgI0xvZygnb21sIGlzICcsIG91dHB1dFsnb21sJ10pCgogICAgICAgIAogICAgICAgIHJldHVybiBvdXRwdXQKICAgIAogICAgZGVmIG1ha2VfdHJhZGVfd2l0aF9hbW91bnQoc2VsZixqeXNfYixodWFfZGlhbiA9IGh1YWRpYW4pOgogICAgICAgIHRyYWRlX2RpY3QgPSBzZWxmLm1ha2VfdHJhZGVfdG8oanlzX2IgLGh1YV9kaWFuID0gaHVhX2RpYW4pCiAgICAgICAgCiAgICAgICAgaWYgbm90IHRyYWRlX2RpY3Q6CiAgICAgICAgICAgIHJldHVybiBOb25lCiAgICAgICAgCiAgICAgICAgc2FsZV9qeXMgPSB0cmFkZV9kaWN0WydzYWxlX2p5cyddCiAgICAgICAgYnV5X2p5cyA9IHRyYWRlX2RpY3RbJ2J1eV9qeXMnXQoKICAgICAgICBidXlfcHJpY2UgPSB0cmFkZV9kaWN0WydidXlfcHJpY2UnXQogICAgICAgIHNhbGVfcHJpY2UgPSB0cmFkZV9kaWN0WydzYWxlc19wcmljZSddCiAgICAgICAgCiAgICAgICAgYnV5X2p5c19zdG9jayA9IGJ1eV9qeXMuYWNjb3VudFsnU3RvY2tzJ10KICAgICAgICBzYWxlX2p5c19zdG9jayA9IHNhbGVfanlzLmFjY291bnRbJ1N0b2NrcyddICogMC45OQoKICAgICAgICBzYWxlX2p5c19iYWxhbmNlID0gc2FsZV9qeXMuYWNjb3VudFsnQmFsYW5jZSddCiAgICAgICAgYnV5X2p5c19iYWxhbmNlID0gYnV5X2p5cy5hY2NvdW50WydCYWxhbmNlJ10KCiAgICAgICAgZGVsdGEgPSB0cmFkZV9kaWN0WydkZWx0YSddCgogICAgICAgIHRoaXNfYnV5anlzX2Nhbl9idXlfc3RvY2s9IGJ1eV9qeXNfYmFsYW5jZSoxLjAgLyBidXlfcHJpY2UgKiAwLjk5CiAgICAgICAgaWYgc2FsZV9qeXNfc3RvY2sgPiAoYnV5X2p5c19zdG9jayArIEJvckUpKjg6CiAgICAgICAgICAgIE9hbW91bnQgPSggc2FsZV9qeXNfc3RvY2sgLSBidXlfanlzX3N0b2NrICkqMy81CiAgICAgICAgICAgICNMb2coIuaIkeimgeaUvuWkp+S6hu+8jOi/measoeS4gOWNleaIkOS6pOeahHN0b2Nr5Li677yaIixPYW1vdW50KQogICAgICAgIGVsc2U6CiAgICAgICAgICAgICNMb2coJ3NhbGUgcHJpY2UgaXM6JyxzYWxlX3ByaWNlLCdidXkgcHJpY2UgaXMnLCBidXlfcHJpY2UsJ2RlbHRhIGlzJywgZGVsdGEpCiAgICAgICAgICAgIHRoaXNfbWQgPSAoIHNhbGVfcHJpY2UgLSBidXlfcHJpY2UgLSBkZWx0YSkKICAgICAgICAgICAgeGlzdSA9IGFicyh0aGlzX21kIC8gKGFicyhkZWx0YSkgKyBidXlfcHJpY2UvYmV0YV9yb2NrKSApCiAgICAgICAgICAgIE9hbW91bnQgPSBpbml0X2Ftb3VudCAqIHhpc3UKICAgICAgICAgICAgCiAgICAgICAgeXV6aGkgPSBjaGVja19uYW1lX2FuZF9Cb3JFKCB0cmFkZV9kaWN0WydzYWxlX2p5c19uYW1lJ10gLHRyYWRlX2RpY3RbJ2J1eV9qeXNfbmFtZSddICkKICAgICAgICBpZiBPYW1vdW50IDwgeXV6aGk6CiAgICAgICAgICAgIE9hbW91bnQgPSB5dXpoaQogICAgICAgIGVsc2U6CiAgICAgICAgICAgIHNob3VsZF9sZXNzX2lzID0gbWluKHRoaXNfYnV5anlzX2Nhbl9idXlfc3RvY2ssc2FsZV9qeXNfc3RvY2ssdHJhZGVfZGljdFsnb21sJ10pCiAgICAgICAgICAgIGlmIE9hbW91bnQgPiBzaG91bGRfbGVzc19pczoKICAgICAgICAgICAgICAgIE9hbW91bnQgPSBzaG91bGRfbGVzc19pcwogICAgICAgICAgICAKICAgICAgICB0cmFkZV9kaWN0WydPYW1vdW50J10gPSBfTihPYW1vdW50LCBhbW91bnRfTikKICAgICAgICB0cmFkZV9kaWN0WydzaG91bGRfbGVzc190aGFuJ10gPSBtaW4oIHRoaXNfYnV5anlzX2Nhbl9idXlfc3RvY2sgLCBzYWxlX2p5c19zdG9jayAsIHRyYWRlX2RpY3RbJ29tbCddKQogICAgICAgIHRyYWRlX2RpY3RbJ3Nob3VsZF9sZXNzX3RoYW5fbGlzdCddID0gWyB0aGlzX2J1eWp5c19jYW5fYnV5X3N0b2NrICwgc2FsZV9qeXNfc3RvY2sgLCB0cmFkZV9kaWN0WydvbWwnXSBdCiAgICAgICAgcmV0dXJuIHRyYWRlX2RpY3QKCmRlZiBtYWtlX3phaWZfbm91bmNlX3Byb2JsZW0oIGxhc3RfdGltZV9zdGFtcCApOgogICAgdGhpc190aW1lX3N0YW1wID0gdGltZS50aW1lKCkKICAgIHRoaXNfdGltZV9jaGEgPSAodGhpc190aW1lX3N0YW1wIC1sYXN0X3RpbWVfc3RhbXAgKSoxMDAwCiAgICAKICAgIGlmIHRoaXNfdGltZV9jaGEgPCAxMDAxIDoKICAgICAgICAjc2xlZXBfaXMgPSBfTiggMTAwMCAtIHRoaXNfdGltZV9jaGEsIDApCiAgICAgICAgc2xlZXBfaXMgPSBfTiggMTAwMSAtIHRoaXNfdGltZV9jaGEsIDApCiAgICAgICAgI0xvZygn5Li65LqG5aSE55CGemFpZueahG5vdW5jZemXrumimO+8jOaIkeS7rOetieS4gOenki4uLicsIF9OKCBzbGVlcF9pcyAsIDIgKSwgJ21zICBjaGFfaXMnLCB0aGlzX3RpbWVfY2hhICkKICAgICAgICBTbGVlcCAoIHNsZWVwX2lzICkKICAgICAgICAKICAgIHJldHVybiB0aW1lLnRpbWUoKQogICAgCmRlZiBjaGVja19uYW1lX2FuZF9Cb3JFKGFfbmFtZSxiX25hbWUpOgogICAgaWYgYV9uYW1lID09ICdCVENUcmFkZScgb3IgYl9uYW1lID09ICdCVENUcmFkZSc6CiAgICAgICAgcmV0dXJuIDAuMDEgCiAgICBlbHNlOgogICAgICAgIHJldHVybiBCb3JFCiAgICAKICAgIAppbXBvcnQganNvbgpsaXN0ZW5lciA9IHt9CgpjbGFzcyBUYWJsZSgpOgogICAgIiIiZG9jc3RyaW5nIGZvciBUYWJsZSIiIgogICAgZGVmIF9faW5pdF9fKHNlbGYpOgogICAgICAgIHNlbGYudGIgPSB7CiAgICAgICAgICAgICJ0eXBlIiA6ICJ0YWJsZSIsCiAgICAgICAgICAgICJ0aXRsZSIgOiAiVGFibGUiLAogICAgICAgICAgICAiY29scyIgOiBbXSwKICAgICAgICAgICAgInJvd3MiIDogW10KICAgICAgICB9CgogICAgZGVmIFNldENvbFJvdyhzZWxmLCBjb2xfaW5kZXgsIHJvd19pbmRleCwgcm93KToKICAgICAgICBpZiAodHlwZShjb2xfaW5kZXgpIGlzIGludCkgYW5kICh0eXBlKHJvd19pbmRleCkgaXMgaW50KSA6CiAgICAgICAgICAgIGlmIChjb2xfaW5kZXggPiBsZW4oc2VsZi50YlsiY29scyJdKSkgb3IgKHJvd19pbmRleCA+IGxlbihzZWxmLnRiWyJyb3dzIl0pKSA6CiAgICAgICAgICAgICAgICBMb2coIue0ouW8lei2heWHuuiMg+WbtO+8gWNvbF9pbmRleDoiLCBjb2xfaW5kZXgsICJyb3dfaW5kZXg6Iiwgcm93X2luZGV4KQogICAgICAgICAgICBlbHNlIDoKICAgICAgICAgICAgICAgIHNlbGYudGJbInJvd3MiXVtyb3dfaW5kZXggLSAxXVtjb2xfaW5kZXggLSAxXSA9IHJvdwogICAgICAgIGVsc2UgOgogICAgICAgICAgICBMb2coImNvbF9pbmRleDoiLCBjb2xfaW5kZXgsICJyb3dfaW5kZXg6Iiwgcm93X2luZGV4KQogICAgICAgICAgICByYWlzZSAiU2V0Q29sUm93IOWPguaVsOmUmeivryEiCgogICAgZGVmIFNldEJ0bihzZWxmLCBjb2xfaW5kZXgsIHJvd19pbmRleCwgY21kLCBuYW1lLCBjYWxsYmFjayk6CiAgICAgICAgZ2xvYmFsIGxpc3RlbmVyCiAgICAgICAgaWYgKHR5cGUoY29sX2luZGV4KSBpcyBpbnQpIGFuZCAodHlwZShyb3dfaW5kZXgpIGlzIGludCkgOgogICAgICAgICAgICBpZiAoY29sX2luZGV4ID4gbGVuKHNlbGYudGJbImNvbHMiXSkpIG9yIChyb3dfaW5kZXggPiBsZW4oc2VsZi50Ylsicm93cyJdKSkgOgogICAgICAgICAgICAgICAgTG9nKCLntKLlvJXotoXlh7rojIPlm7TvvIFjb2xfaW5kZXg6IiwgY29sX2luZGV4LCAicm93X2luZGV4OiIsIHJvd19pbmRleCkKICAgICAgICAgICAgZWxzZSA6CiAgICAgICAgICAgICAgICBzZWxmLnRiWyJyb3dzIl1bcm93X2luZGV4IC0gMV1bY29sX2luZGV4IC0gMV0gPSB7InR5cGUiIDogImJ1dHRvbiIsICJjbWQiIDogY21kLCAibmFtZSIgOiBuYW1lfQogICAgICAgICAgICAgICAgbGlzdGVuZXJbY21kXSA9IGNhbGxiYWNrCiAgICAgICAgZWxzZSA6CiAgICAgICAgICAgIExvZygiY29sX2luZGV4OiIsIGNvbF9pbmRleCwgInJvd19pbmRleDoiLCByb3dfaW5kZXgpCiAgICAgICAgICAgIHJhaXNlICJTZXRDb2xSb3cg5Y+C5pWw6ZSZ6K+vISIKICAgIAogICAgZGVmIFNldFJvd3Moc2VsZiwgcm93X2luZGV4LCBSb3dzKToKICAgICAgICBwYXNzCgogICAgZGVmIFNldENvbHMoc2VsZiwgQ29scyk6CiAgICAgICAgc2VsZi50YlsiY29scyJdID0gQ29scwoKICAgIGRlZiBHZXRSb3dzKHNlbGYsIHJvd19pbmRleCk6CiAgICAgICAgaWYgKHR5cGUocm93X2luZGV4KSBpcyBpbnQpIGFuZCAocm93X2luZGV4IDwgbGVuKHNlbGYudGJbInJvd3MiXSkpIDoKICAgICAgICAgICAgcmV0dXJuIHNlbGYudGJbInJvd3MiXVtyb3dfaW5kZXggLSAxXQogICAgICAgIGVsc2UgOgogICAgICAgICAgICBMb2coIuWPguaVsOmUmeivr++8gSDmiJbogIUg5Y+C5pWw57Si5byV6LaF5Ye66IyD5Zu077yBIikKCiAgICBkZWYgSW5pdChzZWxmLCB0aXRsZSwgY29sX2xlbmd0aCwgcm93X2xlbmd0aCk6ICAKICAgICAgICBzZWxmLnRiWyJ0aXRsZSJdID0gdGl0bGUKICAgICAgICBmb3IgaSBpbiByYW5nZSgxLCByb3dfbGVuZ3RoICsgMSkgOgogICAgICAgICAgICBpZiBpID09IDEgOgogICAgICAgICAgICAgICAgZm9yIG4gaW4gcmFuZ2UoMSwgY29sX2xlbmd0aCArIDEpIDoKICAgICAgICAgICAgICAgICAgICBzZWxmLnRiWyJjb2xzIl0uYXBwZW5kKG4pCiAgICAgICAgICAgIHNlbGYudGJbInJvd3MiXS5hcHBlbmQoW10pCiAgICAgICAgICAgIGZvciBtIGluIHJhbmdlKDEsIGNvbF9sZW5ndGggKyAxKSA6CiAgICAgICAgICAgICAgICBzZWxmLnRiWyJyb3dzIl1baSAtIDFdLmFwcGVuZChzdHIoaSkgKyAiLyIgKyBzdHIobSkpCgoKY2xhc3MgQ3JlYXRlVGFibGVNYW5hZ2VyKCk6CiAgICAiIiJkb2NzdHJpbmcgZm9yIENyZWF0ZVRhYmxlTWFuYWdlciIiIgogICAgZGVmIF9faW5pdF9fKHNlbGYpOiAgICAgICAgIyBDcmVhdGVUYWJsZU1hbmFnZXIg5p6E6YCg5Ye95pWwCiAgICAgICAgc2VsZi50YWJsZXMgPSBbXSAgICAgICAjIOeUqOS6juWCqOWtmCB0YWJsZSDlr7nosaEKICAgIAogICAgZGVmIEdldFRhYmxlKHNlbGYsIGluZGV4KToKICAgICAgICBpZiB0eXBlKGluZGV4KSBpcyBpbnQgOgogICAgICAgICAgICByZXR1cm4gc2VsZi50YWJsZXNbaW5kZXhdCiAgICAgICAgZWxpZiB0eXBlKGluZGV4KSBpcyBzdHIgOgogICAgICAgICAgICBmb3IgaSBpbiByYW5nZShsZW4oc2VsZi50YWJsZXMpKSA6CiAgICAgICAgICAgICAgICBpZiBzZWxmLnRhYmxlc1tpXVsidGl0bGUiXSA9PSBpbmRleDoKICAgICAgICAgICAgICAgICAgICByZXR1cm4gc2VsZi50YWJsZXNbaV0KICAgICAgICBlbHNlIDoKICAgICAgICAgICAgTG9nKCJHZXRUYWJsZeWPguaVsDoiLCBpbmRleCkKICAgICAgICAgICAgcmFpc2UgIkdldFRhYmxlIOWPguaVsOmUmeivr++8gSIKICAgIAogICAgZGVmIEFkZFRhYmxlKHNlbGYsIHRpdGxlLCBjb2xfbGVuZ3RoLCByb3dfbGVuZ3RoKTogICAgIyBjb2xzLCByb3dzCiAgICAgICAgdGIgPSBUYWJsZSgpCiAgICAgICAgdGIuSW5pdCh0aXRsZSwgY29sX2xlbmd0aCwgcm93X2xlbmd0aCkKICAgICAgICBzZWxmLnRhYmxlcy5hcHBlbmQodGIudGIpCiAgICAgICAgcmV0dXJuIHRiCgogICAgZGVmIFVwZGF0ZUNNRChzZWxmKToKICAgICAgICBnbG9iYWwgbGlzdGVuZXIKICAgICAgICBjbWQgPSBHZXRDb21tYW5kKCkKICAgICAgICBpZiBjbWQgOgogICAgICAgICAgICBpZiBsaXN0ZW5lcltjbWRdIDoKICAgICAgICAgICAgICAgIGxpc3RlbmVyW2NtZF0oY21kKQogICAgICAgICAgICBlbHNlIDoKICAgICAgICAgICAgICAgIExvZygi5om+5LiN5Yiw5ZCN5Li677yaIiArIGNtZCArICLnmoTlkb3ku6QiKQogICAgCiAgICBkZWYgTG9nU3RhdHVzKHNlbGYsIGJlZm9yZSwgZW5kKToKICAgICAgICBzZWxmLlVwZGF0ZUNNRCgpCiAgICAgICAgTG9nU3RhdHVzKGJlZm9yZSArICdcbmAnICsganNvbi5kdW1wcyhzZWxmLnRhYmxlcykgKyAnYFxuJyArIGVuZCk=" )


