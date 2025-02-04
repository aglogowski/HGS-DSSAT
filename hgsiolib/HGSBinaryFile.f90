module HGSBinaryFileMod
    implicit none
    private

    integer, parameter :: headerLen = 80

    interface readHGSBinFile1D
        module procedure read_I4_1D, read_R4_1D, read_R8_1D
    end interface

    interface writeHGSBinFile1D
        module procedure write_I4_1D, write_R4_1D, write_R8_1D
    end interface

    public :: readHGSBinFile1D, writeHGSBinFile1D

contains
    subroutine read_I4_1D(fname, nvals, vals, header)
        character(*), intent(in) :: fname
        integer, intent(in) :: nvals
        integer(4), intent(inout) :: vals(:)
        character(*), intent(inout), optional :: header

        integer :: i, istat, iunit
        character(headerLen) :: header_

        open(newunit=iunit, file=fname, status='old', action='read', &
            form='unformatted', iostat=istat)
        ! TODO: check file open status istat
        read(iunit, iostat=istat) header_
        ! TODO: check read status istat
        if (present(header)) then
            header = header_
        endif
        read(iunit, iostat=istat) (vals(i), i = 1,nvals)
        ! TODO: check read status istat
        close(iunit)
    end subroutine

    subroutine read_R4_1D(fname, nvals, vals, header)
        character(*), intent(in) :: fname
        integer, intent(in) :: nvals
        real(4), intent(inout) :: vals(:)
        character(*), intent(inout), optional :: header

        integer :: i, istat, iunit
        character(headerLen) :: header_

        open(newunit=iunit, file=fname, status='old', action='read', &
            form='unformatted', iostat=istat)
        ! TODO: check file open status istat
        read(iunit, iostat=istat) header_
        ! TODO: check read status istat
        if (present(header)) then
            header = header_
        endif
        read(iunit, iostat=istat) (vals(i), i = 1,nvals)
        ! TODO: check read status istat
        close(iunit)
    end subroutine

    subroutine read_R8_1D(fname, nvals, vals, header)
        character(*), intent(in) :: fname
        integer, intent(in) :: nvals
        real(8), intent(inout) :: vals(:)
        character(*), intent(inout), optional :: header

        integer :: i, istat, iunit
        character(headerLen) :: header_

        open(newunit=iunit, file=fname, status='old', action='read', &
            form='unformatted', iostat=istat)
        ! TODO: check file open status istat
        read(iunit, iostat=istat) header_
        ! TODO: check read status istat
        if (present(header)) then
            header = header_
        endif
        read(iunit, iostat=istat) (vals(i), i = 1,nvals)
        ! TODO: check read status istat
        close(iunit)
    end subroutine

    subroutine write_I4_1D(fname, simTime, nvals, vals)
        character(*), intent(in) :: fname
        real(8), intent(in) :: simTime
        integer, intent(in) :: nvals
        integer(4), intent(in) :: vals(:)

        integer :: i, istat, iunit
        character(headerLen) :: header

        open(newunit=iunit, file=fname, status='replace', action='write', &
            form='unformatted', iostat=istat)
        ! TODO: check file open status istat
        write(header, *) simTime
        write(iunit, iostat=istat) header
        ! TODO: check write status istat
        write(iunit, iostat=istat) (vals(i), i = 1,nvals)
        ! TODO: check write status istat
        close(iunit)
    end subroutine

    subroutine write_R4_1D(fname, simTime, nvals, vals)
        character(*), intent(in) :: fname
        real(8), intent(in) :: simTime
        integer, intent(in) :: nvals
        real(4), intent(in) :: vals(:)

        integer :: i, istat, iunit
        character(headerLen) :: header

        open(newunit=iunit, file=fname, status='replace', action='write', &
            form='unformatted', iostat=istat)
        ! TODO: check file open status istat
        write(header, *) simTime
        write(iunit, iostat=istat) header
        ! TODO: check write status istat
        write(iunit, iostat=istat) (vals(i), i = 1,nvals)
        ! TODO: check write status istat
        close(iunit)
    end subroutine

    subroutine write_R8_1D(fname, simTime, nvals, vals)
        character(*), intent(in) :: fname
        real(8), intent(in) :: simTime
        integer, intent(in) :: nvals
        real(8), intent(in) :: vals(:)

        integer :: i, istat, iunit
        character(headerLen) :: header

        open(newunit=iunit, file=fname, status='replace', action='write', &
            form='unformatted', iostat=istat)
        ! TODO: check file open status istat
        write(header, *) simTime
        write(iunit, iostat=istat) header
        ! TODO: check write status istat
        write(iunit, iostat=istat) (vals(i), i = 1,nvals)
        ! TODO: check write status istat
        close(iunit)
    end subroutine
end module
