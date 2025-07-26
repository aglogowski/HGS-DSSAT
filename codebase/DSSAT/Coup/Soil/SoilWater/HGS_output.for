C=======================================================================
C  Dumy reading from HGS, Subroutine
C  Taking flow outputs form HGS and transform them into DSSAT varaibles.
C-----------------------------------------------------------------------
C  REVISION HISTORY
C  02/19/2025 AG and PS
!-----------------------------------------------------------------------
C  Called by: WATBAL
C  Calls    : None
C=======================================================================
      SUBROUTINE process_data (
     &    DAS,
     &    SWDELTS,DRN)

!     ------------------------------------------------------------------
      USE ModuleDefs     !Definitions of constructed variable types, 
                         ! which contain control information, soil
                         ! parameters, hourly weather data.
!     NL defined in ModuleDefs.for

      IMPLICIT NONE
      SAVE
      
      INTEGER DYNAMIC
      INTEGER i, DAS, ios
      integer :: unit_in
      REAL DRAIN
      REAL, DIMENSION(NL),INTENT(OUT) :: DRN 
      REAL, DIMENSION(NL) :: SWDELTS(NL)
!-----------------------------------------------------------------------
      !open the file and ready 10 values of DRN
      
      open(unit=unit_in, 
     &    file='.\data\1_SWDELTS.inp',
     &    status='old', action='read', iostat=ios)
          if (ios /= 0) then
              print *, 'Error opening file:', 
     &        trim('file')
              stop
          end if
          DO i = 0, DAS
              read(unit_in, *, iostat=ios) SWDELTS
                  if (ios /= 0) then
                      print *, 'Error reading DAS ', DAS
                      stop
                  end if
          ENDDO
      close(unit_in)
      
          open(unit=unit_in, 
     &    file='.\data\1_DRN.inp',
     &    status='old', action='read', iostat=ios)
          if (ios /= 0) then
              print *, 'Error opening file:', 
     &        trim('file')
              stop
          end if
          DO i = 1, DAS
              read(unit_in, *, iostat=ios) DRN
                  if (ios /= 0) then
                      print *, 'Error reading DAS ', DAS
                      stop
                  end if
                  
          ENDDO
      close(unit_in)
      END SUBROUTINE process_data 
      
      SUBROUTINE hgs_data(
     &    DAS, SW, DLAYR, NLAYR,
     &    SWDELTS,DRN, DRAIN)

!     ------------------------------------------------------------------
      USE ModuleDefs     !Definitions of constructed variable types, 
                         ! which contain control information, soil
                         ! parameters, hourly weather data.
!     NL defined in ModuleDefs.for

      IMPLICIT NONE
      SAVE
      
      INTEGER DYNAMIC  
      INTEGER i, DAS, ios, L, NLAYR
      integer :: unit_in
      character*80 file_name, full_path, DAS_con
      REAL DRAIN
      REAL, DIMENSION(NL),INTENT(OUT) :: DRN 
      REAL, DIMENSION(NL) :: SWDELTS(NL)
      REAL, DIMENSION(NL) ::SW
      REAL, DIMENSION(NL) ::SWTEMP
      REAL, DIMENSION(NL) :: DLAYR
!-----------------------------------------------------------------------
      !open the file and ready 10 values of DRN
      file_name = '.\coup_data\1_'
          write(DAS_con, '(I0)') DAS
          full_path=TRIM(file_name) // TRIM(DAS_con) // '_DRN.inp' !
!          print *, full_path
          open(unit=unit_in, 
     &        file=full_path ,
     &        status='old', action='read', iostat=ios)
              if (ios /= 0) then
                  print *, 'Error opening file:', 
     &            trim('file')
                  stop
              end if 
              read(unit_in, *, iostat=ios) DRN
                  if (ios /= 0) then
                      print *, 'Error reading DAS ', DAS
                      stop
                  end if
          
              close(unit_in)
              
              Do L=1, 10
                  
                  SWTEMP(L)=SW(L)+DRN(L)/DLAYR(L)-DRN(L+1)/DLAYR(L)
                  SWDELTS(L)=SWTEMP(L)-SW(L)
              enddo
              DRAIN = DRN(NLAYR)
!              print *, "DRAIN"          
!              print *, DRAIN 
!              print *, "SWDELTS"
!              print *, SWDELTS               
              
      
      END SUBROUTINE hgs_data 
      
      SUBROUTINE wait_for_file(filename)
      implicit none
      character(len=*), intent(in) :: filename
      logical :: file_exists
      integer :: sleep_time 
      sleep_time = 5  ! seconds to wait between checks

      print *, "Waiting for file: ", trim(filename)

      do
          inquire(file=trim(filename), exist=file_exists)
          if (file_exists) then
              print *, "File found: ", trim(filename)
              exit
          else
              call sleep(sleep_time)
          end if
      end do
      end subroutine wait_for_file
      
      subroutine log_data(values)
      real values(20)
      integer call_count
      integer i, unit
      character*100 filename
      save call_count

      data call_count /0/
      call_count = call_count + 1
      filename = 'RWU.txt'
      unit = 99

c     Open file in append mode
      open(unit=unit, file=filename,
     &     status='unknown', position='append', action='write')

c     Write the call count and values array
      write(unit, '(I5, 1X, 20F8.3)') call_count, values

      close(unit)
      return
      end subroutine
!-----------------------------------------------------------------------
!     SNOWFALL VARIABLE DEFINITIONS:
!-----------------------------------------------------------------------
! RAIN    Precipitation depth for current day (mm)
! SNOMLT  Daily Snowmelt (mm/d)
! SNOW    Snow accumulation (mm)
! TMAX    Maximum daily temperature (�C)
! WATAVL  Water available for infiltration or runoff (rainfall plus 
!           irrigation) (mm/d)
!-----------------------------------------------------------------------

! CROP    Crop identification code 
! ERRNUM  Error number for input 
! FILEIO  Filename for input file (e.g., IBSNAT35.INP) 
! FOUND   Indicator that good data was read from file by subroutine FIND (0 
!           - End-of-file encountered, 1 - NAME was found) 
! ICWD    Initial water table depth (cm)
! LINC    Line number of input file 
! LL(L)   Volumetric soil water content in soil layer L at lower limit
!          (cm3 [water] / cm3 [soil])
! LNUM    Current line number of input file 
! LUNIO   Logical unit number for FILEIO 
! NLAYR   Actual number of soil layers 
! SECTION Section name in input file 
! SW(L)   Volumetric soil water content in layer L
!          (cm3 [water] / cm3 [soil])
! ActWTD  Depth to water table (cm)
!-----------------------------------------------------------------------
!-----------------------------------------------------------------------
!     UP_FLOW VARIABLE DEFINITIONS: updated 2/19/2004
!-----------------------------------------------------------------------
! DBAR         
! DLAYR(L)    Thickness of soil layer L (cm)
! DUL(L)      Volumetric soil water content at Drained Upper Limit in soil 
!               layer L (cm3[water]/cm3[soil])
! ESW(L)      Plant extractable soil water by layer (= DUL - LL)
!              (cm3[water]/cm3[soil])
! FLOWFIX     Adjustment amount for upward flow calculations to prevent a 
!               soil layer from exceeding the saturation content (cm3/cm3)
! GRAD         
! IST         Beginning soil layer for upward flow calculations (=1 for 
!               layers 1 through 5, =2 for lower layers) 
! LL(L)       Volumetric soil water content in soil layer L at lower limit
!              (cm3 [water] / cm3 [soil])
! NLAYR       Actual number of soil layers 
! SAT(L)      Volumetric soil water content in layer L at saturation
!              (cm3 [water] / cm3 [soil])
! SW(L)       Volumetric soil water content in layer L
!              (cm3 [water] / cm3 [soil])
! SW_AVAIL(L) Soil water content in layer L available for evaporation, 
!               plant extraction, or movement through soil
!               (cm3 [water] / cm3 [soil])
! SW_INF(L)   Soil water content in layer L including computed upward flow
!              (cm3 [water] / cm3 [soil])
! SWDELTU(L)  Change in soil water content due to evaporation and/or upward 
!               flow in layer L (cm3 [water] / cm3 [soil])
! SWOLD       Previous soil water content prior to capillary flow from 
!               layer (cm3/cm3)
! SWTEMP(L)   Soil water content in layer L (temporary value to be modified 
!               based on drainage, root uptake and upward flow through soil 
!               layers). (cm3/cm3)
! THET1       Soil water content above the lower limit (LL) for an upper 
!               layer of soil for water flow from a lower layer (cm/cm)
! THET2       Soil water content above the lower limit (LL) for a lower 
!               layer of soil for water flow into an upper layer (cm/cm)
! UPFLOW(L)   Movement of water between unsaturated soil layers due to soil 
!               evaporation: + = upward, -- = downward (cm/d)
!-----------------------------------------------------------------------
!     WBSUM VARIABLE DEFINITIONS:
!-----------------------------------------------------------------------
! CRAIN     Cumulative precipitation (mm)
! DLAYR(L)  Soil thickness in layer L (cm)
! DRAIN     Drainage rate from soil profile (mm/d)
! NL        Maximum number of soil layers = 20 
! NLAYR     Actual number of soil layers 
! RAIN      Precipitation depth for current day (mm)
! RUNOFF    Calculated runoff (mm/d)
! SW(L)     Volumetric soil water content in layer L
!             (cm3 [water] / cm3 [soil])
! TDRAIN    Cumulative daily drainage from profile (mm)
! TRUNOF    Cumulative runoff (mm)
! TSW       Total soil water in profile (cm)
! TSWINI    Initial soil water content (cm)
!-----------------------------------------------------------------------
!     WTDEPT VARIABLE DEFINITIONS:
!-----------------------------------------------------------------------
! DLAYR(L) Soil thickness in layer L (cm)
! DS(L)    Cumulative depth in soil layer L (cm)
! NL       Maximum number of soil layers = 20 
! NLAYR    Actual number of soil layers 
! SAT(L)   Volumetric soil water content in layer L at saturation
!            (cm3 [water] / cm3 [soil])
! SW(L)    Volumetric soil water content in layer L (cm3[water]/cm3[soil])
! WTDEP    Water table depth  (cm)
! SATFRAC   Fraction of layer L which is saturated
!-------------