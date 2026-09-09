import React from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'react-native';

export default function Layout(){
  return (
    <>
      <StatusBar barStyle="dark-content" backgroundColor="#F6F7FB" />
      <Stack screenOptions={{
        headerTitleAlign:'center',
        headerShadowVisible:false,
        headerStyle:{backgroundColor:'#F6F7FB'},
        headerTintColor:'#101828',
        headerTitleStyle:{fontWeight:'800'},
        contentStyle:{backgroundColor:'#F6F7FB'},
        animation:'slide_from_right'
      }}>
        <Stack.Screen name="index" options={{headerShown:false}} />
        <Stack.Screen name="courses" options={{title:'Courses'}} />
        <Stack.Screen name="practice" options={{title:'Practice'}} />
        <Stack.Screen name="progress" options={{title:'Progress'}} />
        <Stack.Screen name="about" options={{title:'About'}} />
      </Stack>
    </>
  );
}