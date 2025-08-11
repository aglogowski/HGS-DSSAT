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
      INTEGER :: unit_in
      REAL DRAIN
      REAL, DIMENSION(NL),INTENT(OUT) :: DRN 
      REAL, DIMENSION(NL) :: SWDELTS(NL)
!-----------------------------------------------------------------------
      !open the file and ready 10 values of DRN
      
      OPEN(unit=unit_in, 
     &    file='.\data\1_SWDELTS.inp',
     &    status='old', action='read', iostat=ios)
          IF (ios /= 0) THEN
              PRINT *, 'Error opening file:', 
     &        trim('file')
              STOP
          END IF 
          DO i = 0, DAS
              READ(unit_in, *, iostat=ios) SWDELTS
                  IF (ios /= 0) THEN
                      PRINT *, 'Error reading DAS ', DAS
                      STOP
                  END IF
          ENDDO
      CLOSE(unit_in)
      
          OPEN(unit=unit_in, 
     &    file='.\data\1_DRN.inp',
     &    status='old', action='read', iostat=ios)
          IF (ios /= 0) THEN
              PRINT *, 'Error opening file:', 
     &        trim('file')
              STOP
          END IF
          DO i = 1, DAS
              READ(unit_in, *, iostat=ios) DRN
                  IF (ios /= 0) THEN
                      PRINT *, 'Error reading DAS ', DAS
                      STOP
                  END IF
                  
          ENDDO
      CLOSE(unit_in)
      END SUBROUTINE process_data 
c     watbal when pyHGSDSSAT ready      
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
      INTEGER i, DAS, ios, L, NLAYR, DAS_tmp
      INTEGER :: unit_in
      CHARACTER*80 file_name, full_path, DAS_con
      REAL DRAIN
      REAL, DIMENSION(NL),INTENT(OUT) :: DRN 
      REAL, DIMENSION(NL) :: SWDELTS(NL)
      REAL, DIMENSION(NL) ::SW
      REAL, DIMENSION(NL) ::SWTEMP
      REAL, DIMENSION(NL) :: DLAYR
!-----------------------------------------------------------------------
      !open the file and ready 10 values of DRN
      file_name = '.\data\'
          DAS_tmp=DAS-1
          WRITE(DAS_con, '(I0)') DAS_tmp
          full_path= TRIM(file_name) //'DRN_'//TRIM(DAS_con) // '.inp' !
          print *, full_path
10        CONTINUE
           ! --- Call Python script after CONTINUE ---
          !CALL execute_command_line("python3 into_dssat.py")
          ! Or use this if you're using older Fortran or Windows:
          ! CALL system("python into_dssat.py")
          OPEN(unit=unit_in, file=full_path, status='old',
     &        action='read', iostat=ios)

          IF (ios /= 0) THEN
C              PRINT *, 'File not found. Retrying in 5 second...'
C              CALL SLEEP(1)
              GOTO 10
         
          END IF
20        CONTINUE
              READ(unit_in, *, iostat=ios) DRN
                  IF (ios /= 0) THEN
                      PRINT *, 'Error reading DAS ', DAS
                      GOTO 20
                  END IF
          
              CLOSE(unit_in)
              
              DO L=1, 10
                  
                  SWTEMP(L)=SW(L)+DRN(L)/DLAYR(L)-DRN(L+1)/DLAYR(L)
                  SWDELTS(L)=SWTEMP(L)-SW(L)
              ENDDO
              DRAIN = DRN(NLAYR)
!              print *, "DRAIN"          
!              print *, DRAIN 
!              print *, "SWDELTS"
!              print *, SWDELTS               
              
      
      END SUBROUTINE hgs_data 
c     call CSM end of daily loop            
      SUBROUTINE wait_for_file(filename)
      IMPLICIT NONE 
      CHARACTER(LEN=*), INTENT(IN) :: filename
      LOGICAL :: file_exists
      INTEGER :: sleep_time 
      sleep_time = 5  ! seconds to wait between checks

      PRINT *, "Waiting for file: ", trim(filename)

      DO
          INQUIRE (file=trim(filename), exist=file_exists)
          IF (file_exists) THEN
              PRINT *, "File found: ", trim(filename)
              EXIT
          ELSE
              CALL sleep(sleep_time)
          END IF
      END DO
      END SUBROUTINE wait_for_file
c     call SPsubs end of XTRACT (inside)    
     
      subroutine write_to_file(data, filename)
      implicit none
      real, intent(in) :: data(20)
      character(len=*), intent(in) :: filename
      character(len=100) :: full_filename
      integer :: unit, ios, day_counter, i
      character(len=200) :: line
      logical :: file_exists
      integer :: last_day

      ! Create the full file name with .txt extension
      full_filename = './data/' // trim(filename) // '.txt'

      ! Assign a unit number and open the file in append mode
      inquire(file=full_filename, exist=file_exists)

      if (file_exists) then
          ! File exists, read to get the last day counter
          open(unit=10, file=full_filename, status='old', action='read',
     &         position='rewind')
          last_day = 0
          do
              read(10, '(A)', iostat=ios) line
              if (ios /= 0) exit
              read(line, *, iostat=ios) day_counter
              if (ios == 0) last_day = day_counter
          end do
          close(10)
          day_counter = last_day + 1
      else
        ! File does not exist yet
        day_counter = 1
      end if

      ! Open file for appending new line
      open(unit=11, file=full_filename, status='unknown',
     &     action='write', position='append')

      ! Write day counter followed by the data values
      write(11, '(I5, 1X, 20F10.4)') day_counter, data*10

      close(11)
      end subroutine write_to_file

c     call WATBAL end of End of IF block for PUDDLE   
      subroutine create_empty_file(value)
      implicit none
      integer, intent(in) :: value
      character(len=100) :: filename
      integer :: unit

    ! Convert DAS to string and form filename
      write(filename, '(I0,A)') value, '.txt'

    ! Use a unique unit number (e.g., 10)
      unit = 10

    ! Open the file for writing (will create or overwrite it)
      open(unit=unit, file=filename, status='replace', action='write')
      close(unit)

    !  print *, 'Created file: ', trim(filename)
      end subroutine create_empty_file
      
     
     