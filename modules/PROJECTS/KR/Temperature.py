# -*- coding: utf-8 -*-
"""Temperature

Automatically generated by coLaboratory.

Original file is located at
    https://drive.google.com/a/google.com/file/d/0B-tgNa6DYK2WN2xiOFIzaFhlZ0k/view?usp=drivesdk

###############

**ATE LIBRARY**
###############

These are functions that are imported from the ATE library. 
Many of these functions are to be used across this algorithm
"""

import numpy as np
import pandas as pd

def expfunc(x, a, b, c):
    return a*np.exp(b*x)+c
  
def printl ():
  print "test"
  
def getMean(arr):
  return np.mean(arr)

def getMin(arr):
  print "blah"
  return np.min(arr)

def getNumOfDigitsInInt(num):
  return len(str(num))

def addBiasToData(dataSet, biasAmount):
#   cnt = 0
  dataSet2 =[]
  for val in dataSet:
    dataSet2.append(float(val+biasAmount))
#     cnt +=1
  return dataSet2

#Expecting an array of arryas of same length
def avgAllArraysByIndex (allArrays):
  avg_allArrays = []
  allTempSum = 0
  for i in range(0,len(allArrays[0])):
    for array in allArrays:
      allTempSum += array[i]
    avgVal = allTempSum/len(allArrays)
    avg_allArrays.append(avgVal)
    allTempSum = 0
  return avg_allArrays

"""#####################

TEMPERATURE ALGORITHM

#####################

This is the core testing Algorithm.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import StringIO
from scipy import optimize

INVALID_NUM = -999
def findMaxPointsForFit(x_axis, y_axis):
  rateToFindFit = -10*(getNumOfDigitsInInt(len(x_axis)))
  end = range(len(x_axis)-1,-1,rateToFindFit)
  maxIndx = 0;
  isFitMaximized = False
  foundSolution = False
  currentSolution = end[maxIndx]
  while not isFitMaximized:
    try:
#       print "On this iteration: ", end[maxIndx]
      popt, pcov = sp.optimize.curve_fit(expfunc, x_axis[0:end[maxIndx]], y_axis[0:end[maxIndx]] , p0=(-1, 1e-6, 1))
      foundSolution = True
      if (foundSolution and rateToFindFit == -1) or (foundSolution and maxIndx==0):
#         print "GOT THE MAXIMUM"
        isFitMaximized = True;
      else:
        rateToFindFit = int(rateToFindFit/2)
        currentSolution = end[maxIndx]
        end = range(end[maxIndx-1],end[maxIndx],rateToFindFit)
        if currentSolution not in end:
          end.append(currentSolution)
        maxIndx = 0;
#         print "Here is the new end:" ,end
    except RuntimeError:
      foundSolution = False;
      isFitMaximized = False;
      maxIndx +=1
#   print "The Solution on this Index: ", currentSolution
  return currentSolution

def findBestExpFit (x_axis, y_axis):
  maxIndex = findMaxPointsForFit(x_axis,y_axis)
  popt, pcov = sp.optimize.curve_fit(expfunc, x_axis[0:maxIndex], y_axis[0:maxIndex] , p0=(-1, 1e-6, 1))
  return popt, pcov , maxIndex

def getSteadyState (data, numOfLastPoints = 5):
  ss = np.mean (data[len(data)-numOfLastPoints+1:])
  return ss

def getTimeConstantIdx (data, data_ss, timeConstant = 0.632):
  data_tc = timeConstant*(data_ss - data[0])+data[0]
  idx = 0;
  for val in data:
    if data_tc > val:
      idx += 1
  if idx == len(data):
    idx = idx-1
  return idx

def getIndexOfRaise (data, amtToLookAdvance = 5, thresholdForRise = 0.1):
  allSlopes = []
  findIndex = True
  startIdx = INVALID_NUM
  try:
#     print "Test"
    for i in range(0, len(data)):
      findIndex = True
#       print "On Index: ", i
      for j in range(1, amtToLookAdvance):
        nextIdx = i+j
        currSlope = data[nextIdx]-data[i]
#         print "On Future Index: ", nextIdx, " With Difference: ", currSlope        
        if currSlope < thresholdForRise:
          findIndex = False
          break;
      if (findIndex):
        startIdx = i
        break
  except IndexError:
    print "ERROR Trying To find the rate of rise"
  return startIdx

def flipArray(arr):
#   print "FlipArray"
#   print arr
  temp = []
  for i in range(len(arr)-1,-1,-1):
#     print i
    temp.append(arr[i])
  return temp

def getThermValueFrmOhm (resistance):
  lookUpTable = [[-14.24,-13.66,-13.08,-12.51,-11.94,-11.37,-10.81,-10.26,-9.71,-9.16,-8.62,-8.08,-7.55,-7.02,-6.5,-5.98,-5.47,-4.96,-4.45,-3.95,-3.46,-2.96,-2.47,-1.99,-1.51,-1.03,-0.56,-0.09,0.36,0.82,1.28,1.73,2.18,2.62,3.06,3.5,3.93,4.36,4.78,5.21,5.62,6.04,6.45,6.86,7.26,7.66,8.06,8.45,8.84,9.23,9.61,9.99,10.37,10.74,11.11,11.48,11.84,12.21,12.56,12.92,13.27,13.62,13.97,14.31,14.65,14.99,15.32,15.65,15.98,16.31,16.63,16.95,17.27,17.59,17.9,18.21,18.52,18.83,19.13,19.43,19.73,20.03,20.32,20.61,20.9,21.19,21.48,21.76,22.04,22.32,22.6,22.87,23.14,23.42,23.69,23.95,24.22,24.48,24.74,25.0,25.26,25.52,25.77,26.03,26.28,26.53,26.78,27.03,27.27,27.52,27.76,28.0,28.24,28.48,28.72,28.95,29.19,29.42,29.66,29.89,30.12,30.35,30.58,30.81,31.03,31.26,31.48,31.71,31.93,32.15,32.38,32.6,32.82,33.04,33.26,33.47,33.69,33.91,34.13,34.34,34.56,34.78,34.99,35.21,35.42,35.63,35.85,36.06,36.28,36.49,36.7,36.92,37.13,37.34,37.56,37.77,37.98,38.2,38.41,38.63,38.84,39.05,39.27,39.48,39.7,39.91,40.13,40.35,40.56,40.78,41.0,41.22,41.44,41.66,41.88,42.1,42.32,42.54,42.77,42.99,43.21,43.44,43.67,43.9,44.12,44.35,44.58,44.82,45.05,45.28,45.52,45.75,45.99,46.23,46.47,46.71,46.96,47.2,47.45,47.69,47.94,48.19,48.44,48.7,48.95,49.21,49.47,49.73,49.99,50.25,50.52,50.79,51.05,51.33,51.6,51.87,52.15,52.43,52.71,52.99,53.28,53.57,53.85,54.15,54.44,54.74,55.04,55.34,55.64,55.95,56.25,56.56,56.88,57.19,57.51,57.83,58.16,58.48,58.81,59.14,59.48,59.82,60.16,60.5,60.84,61.19,61.55,61.9,62.26,62.62,62.98,63.35,63.72,64.09,64.47,], \
                 [12418096.31,6196898.157,4122929.491,3086166.357,2464094.32,2049314.746,1753098.513,1530900.0,1358109.83,1219875.925,1106756.739,1012507.373,932757.1477,864388.4227,805145.8983,753300.0,707561.5788,666904.9152,630521.7879,597782.6542,568161.3559,541228.3695,516641.6391,494100.0,473365.274,454225.4327,436500.3641,420044.2113,404722.8989,390420.5898,377043.3165,364500.0,352718.913,341630.7894,331174.5024,321300.8192,311960.8166,303110.8939,294716.2571,286740.0,279154.1322,271929.4742,265039.6784,258464.1848,252180.9175,246169.8161,240415.4944,234900.0,229610.5357,224532.637,219653.0432,214961.9311,210447.8312,206100.182,201911.3478,197871.4286,193973.9293,190210.8182,186574.6525,183060.2949,179661.1551,176371.1058,173186.0487,170100.0,167109.4192,164209.4565,161395.5815,158664.9355,156013.4337,153437.2512,150934.0661,148500.0,146133.0261,143830.0205,141588.0472,139405.447,137279.5341,135207.7796,133188.8202,131220.0,129300.1214,127427.0661,125598.8337,123814.4362,122072.0219,120369.8392,118707.0719,117081.8182,115493.359,113940.1966,112420.9112,110934.908,109480.86,108057.5069,106664.3576,105300.0,103964.0022,102655.2679,101372.7544,100116.1062,98884.34055,97676.52161,96492.3581,95330.76923,94191.50079,93073.72664,91976.6587,90900.09102,89843.27565,88805.49842,87786.5942,86785.71429,85802.71723,84836.96465,83887.84616,82955.25131,82038.59726,81137.32626,80251.35422,79380.0,78523.19488,77680.43486,76851.23706,76035.55292,75232.91891,74442.89058,73665.43661,72900.0,72146.55948,71404.70962,70674.06127,69954.60639,69245.9697,68547.79076,67860.07282,67182.35294,66514.64096,65856.60536,65207.92741,64568.6256,63938.39133,63316.92773,62704.2607,62100.0,61504.1758,60916.51307,60336.74698,59764.91333,59200.75483,58644.02359,58094.76019,57552.63158,57017.68107,56489.67754,55968.39814,55453.88978,54945.93525,54444.32506,53949.1091,53460.0,52977.04935,52500.06068,52028.84435,51563.45411,51103.70461,50649.41685,50200.64639,49757.14286,49318.96279,48885.93746,48457.90381,48034.91961,47616.82508,47203.46581,46794.90048,46390.90909,45991.55084,45596.67948,45206.15354,44820.03277,44438.17826,44060.45559,43686.92487,43317.3913,42951.91516,42590.36861,42232.62791,41878.75344,41528.62344,41182.11997,40839.30339,40500.0,40164.27008,39832.00108,39503.0839,39177.57866,38855.37782,38536.37718,38220.63653,37908.0,37598.52717,37292.11824,36988.67639,36688.26081,36390.77592,36096.12901,35804.3788,35515.38462,35229.20483,34945.7504,34664.93487,34386.81608,34111.30856,33838.32935,33567.93569,33300.0,33034.57912,32771.59314,32510.96444,32252.74921,31996.87062,31743.25401,31491.95494,31242.85714,30996.01573,30751.35861,30508.81572,30268.44148,30030.16643,29793.92308,29559.76513,29327.58621,29097.43956,28869.25985,28642.98353,28418.66313,28196.23561,27975.63962,27756.927,27540.0,27324.90998,27111.59744,26900.00449,26690.18177,26482.07177,26275.61853,26070.87196,25867.74194,25666.2779,25466.42548,25268.1317,25071.44529,24876.31361,24682.68539,24490.60864]]
  x = flipArray(lookUpTable[1])
  y = flipArray(lookUpTable[0])
  temp = np.interp(resistance, x, y)
  return round(temp,3)
  
def dtsAlgo(df, stepStartTime = '0', stepEndTime = '-1'):
  
  #import data
  startIndex = 0
  endIndex = -1
  totalMainSensorValues = np.array((df['MainTempSensor']), dtype=float)
  if(stepStartTime not in '0'):
    startIndex = int(df[df['Time'] == stepStartTime].index.tolist()[0])  
  else:
    startIndex = getIndexOfRaise(totalMainSensorValues)    
  if(stepEndTime not in '-1'):
    endIndex = int(df[df['Time'] == stepEndTime].index.tolist()[0])  
   
  timeValue = np.array((df['Time']), dtype=float)
  #   timeStep = timeValue[3]-timeValue[2]
  totalMainSensorValues = np.array((df['MainTempSensor']), dtype=float)
  
  if startIndex == INVALID_NUM:
    idleTime = INVALID_NUM
    idleTimeTemepratureRise = INVALID_NUM
  else:
    idleTime = timeValue[startIndex]-timeValue[0]
    idleTimeTemepratureRise = totalMainSensorValues[startIndex] - totalMainSensorValues[0]

  df = df [startIndex:endIndex]
  timeValue = np.array((df['Time']), dtype=float)
  totalMainSensorValues = np.array((df['MainTempSensor']), dtype=float)
  heaterValues = np.array((df['Heater_Temp']), dtype=float)
  ambientValues = np.array((df['Ambient_Temp']), dtype=float)

  internalThermValues_res = []
  internalThermValues_res.append(np.array((df['Thermistor_1']), dtype=float))
  internalThermValues = []
  
  #If the thermistor values are in resistance form
  for thermistor in internalThermValues_res:
    allValues = []
    for val in thermistor:
      allValues.append(getThermValueFrmOhm(val))
    
#     print allValues
    internalThermValues.append(allValues)
#   print internalThermValues
  
  #Changes time to start from 0
  timeValue = addBiasToData(timeValue,-1*timeValue[0])
  lastTime = timeValue [len(timeValue)-1]
  
  #Finding Average Internal Temperature
#   avg_internalTemp = avgAllArraysByIndex(internalThermValues)
  avg_internalTemp = internalThermValues[0]
  #Compensating Main Temperature for Internal Temperature
  deltaInInternalTemp = addBiasToData (avg_internalTemp,-1*avg_internalTemp[0])
  compMainTempSensorVal = []
  cnt = 0
  for val in deltaInInternalTemp:
    compMainTempSensorVal.append(totalMainSensorValues[cnt] - val)
    cnt +=1

  # Total Raw TMP112 Fit
  popt, pcov , maxTtlIndex = findBestExpFit(timeValue,totalMainSensorValues)
  
  xx = np.linspace(0, lastTime*5,lastTime*10 )
  fit = expfunc(xx, *popt)

  # Compensated TMP112 Fit with Internal Heatings
  popt, pcov , maxCompTtlIndex = findBestExpFit(timeValue,compMainTempSensorVal)
  xx = np.linspace(0, lastTime*5,lastTime*10 )
  fit_comp = expfunc(xx, *popt)
  
  rawTemp_ss = getSteadyState (fit)
  compTemp_ss = getSteadyState (fit_comp)
  
  rawTemp_tc = timeValue [getTimeConstantIdx(totalMainSensorValues,rawTemp_ss )]
  compTemp_tc = timeValue [getTimeConstantIdx(compMainTempSensorVal,compTemp_ss)]
  
  rawTemp_st = xx [getTimeConstantIdx(fit,rawTemp_ss , 0.98)]
  compTemp_st = xx [getTimeConstantIdx(fit_comp,compTemp_ss, 0.98)]
  
  # Constant for function: a*np.exp(c*x)+d

  output_dict = {}
  output_dict["IDLE_TIME"] = round(float(idleTime),3)
  output_dict["IDLE_TIME_TEMP_RISE"] = round(float(idleTimeTemepratureRise),3)
  output_dict["EXP_CURVE_CONSTANT_A"] = popt[0]
  output_dict["EXP_CURVE_CONSTANT_B"] = popt[1]
  output_dict["EXP_CURVE_CONSTANT_C"] = popt[2]
  output_dict["RAW_STEADY_STATE_VALUE"] = round(rawTemp_ss,3)
  output_dict["RAW_TIME_CONSTANT"] = round(rawTemp_tc,3)
  output_dict["RAW_SETTLE_TIME"] = round(rawTemp_st,3)
  output_dict["COMP_STEADY_STATE_VALUE"] = round(compTemp_ss,3)
  output_dict["COMP_TIME_CONSTANT"] = round(compTemp_tc,3)
  output_dict["COMP_SETTLE_TIME"] = round(compTemp_st,3)
  output_dict["HEATER_PLATE_STD_DEV"] = round(np.std(heaterValues),3)
  output_dict["HEATER_PLATE_MAX"] = round(np.max(heaterValues),3)
  output_dict["HEATER_PLATE_MIN"] = round(np.min(heaterValues),3)
  output_dict["AMBIENT_STD_DEV"] = round(np.std(ambientValues),3)
  output_dict["AMBIENT_MAX"] = round(np.max(ambientValues),3)
  output_dict["AMBIENT_MIN"] = round(np.min(ambientValues),3)
  output_dict["APPLIED_STEP"] = round(np.mean(heaterValues)-np.mean(ambientValues),3)
  output_dict["PERCEIVED_STEP"] = round(totalMainSensorValues[len(totalMainSensorValues)-1]-totalMainSensorValues[0],3)
  output_dict["INTERNAL_THERM_CONVERTED"] = internalThermValues
  output_dict["TMP112_FINAL_VALUE"] = round(totalMainSensorValues[len(totalMainSensorValues)-1],3)
  output_dict["TMP112_MAX"] = round(np.max(totalMainSensorValues),3)
  output_dict["TMP112_MIN"] = round(np.min(totalMainSensorValues),3)
  output_dict["TMP112_STARTING_VALUE"] = round(totalMainSensorValues[0],3)
  output_dict["THERMISTOR_STD_DEV"] = round(np.std(internalThermValues),3)
  output_dict["THERMISTOR_MAX"] = round(np.max(internalThermValues),3)
  output_dict["THERMISTOR_MIN"] = round(np.min(internalThermValues),3)
  
  
  #   Plotting for sanity
#   import matplotlib.pyplot as plt
#   plt.figure(figsize=(40, 5), dpi=80)
#   plt.plot(timeValue,totalMainSensorValues, color = 'g')
#   plt.plot(timeValue,compMainTempSensorVal, color = 'b')
#   plt.plot(timeValue,avg_internalTemp, color = 'black')
#   plt.plot(xx, fit,color = 'g')
#   plt.plot(xx, fit_comp, color = 'b')
#   plt.xlim((0,100))
#   plt.ylim((-5,5))
#   plt.show() 
  
  return output_dict

# df = pd.read_csv('Temperature1.csv',dtype=str)
# result = dtsAlgo(df)
# print result
"""###############################

# **ALGORITHM INPUT**
###############################

1) **dataframe df**:

> A datafrmae of all the recorded content from the test. The format for the data should look like:

> > *Time,Heater_Temp,Ambient_Temp,MainTempSensor,Internal_Thermistor_1,Thermistor_2,Thermistor_3,Thermistor_4,Thermistor_5,Thermistor_6,Thermistor_7*

> >*1499819022.93,26.77,26.51,30.25,34.18,34.18,32.99,33.26,33.39,33.80,33.83*


2) **stepStartTime = 0**:
> You can specify the time at which the heater plate started touching the DUT. If not specifed, it will default to time 0

3) **stepEndTime = [lastIndex]**:
> You can specify the time at which the test ended. If not specifed, it will default to the last entry in the file.
"""

## ANYTHING AFTER THIS MARK IS NOT PART OF THE ALGO ##
## This is all meant for testing purposes ##
# from colabtools import sheets
# import numpy as np

# # Enter your Google Sheet link here
# link_to_sheet = 'https://docs.google.com/spreadsheets/d/1NCF_yE86unNCvRZ87lORjtgQQXjUVkA2SbF0vGI0Zyg/edit#gid=539987777' #@param
# sheet_id = sheets.get_spreadsheet_id(link_to_sheet)
# worksheet_id = sheets.get_worksheet_id(link_to_sheet)

# # Turning the sheet into a dataframe
# orig_df = sheets.get_cells(sheet_id, worksheet_id)
# orig_df_columnNames = orig_df.iloc[0]
# orig_df = orig_df.rename(columns=orig_df_columnNames)
# orig_df = orig_df[1:] 
# df = orig_df

# # stepStartTime = '1499819107.12' #@param
# # stepEndTime = '-1' #@param

# result = dtsAlgo(df)
# for thing in result:
#   print thing,result[thing]
