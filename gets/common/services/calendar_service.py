# common/services/calendar_service.py
from datetime import datetime, timedelta, date
import calendar
from django.utils.safestring import mark_safe
from common.models import Activite

class CalendarService:
    @staticmethod
    def get_month_calendar(year, month):
        """Generate a calendar for a specific month with activities"""
        cal = Calendar(year, month)
        html_calendar = cal.formatmonth(withyear=True)
        
        prev_month = CalendarService.get_prev_month_link(date(year, month, 1))
        next_month = CalendarService.get_next_month_link(date(year, month, 1))
        
        return {
            'calendar': mark_safe(html_calendar),
            'prev_month': prev_month,
            'next_month': next_month,
        }
    
    @staticmethod
    def get_prev_month_link(d):
        """Calculate previous month for navigation"""
        first = d.replace(day=1)
        prev_month = first - timedelta(days=1)
        return f'month={prev_month.year}-{prev_month.month}'
    
    @staticmethod
    def get_next_month_link(d):
        """Calculate next month for navigation"""
        days_in_month = calendar.monthrange(d.year, d.month)[1]
        last = d.replace(day=days_in_month)
        next_month = last + timedelta(days=1)
        return f'month={next_month.year}-{next_month.month}'
    
    @staticmethod
    def get_date_from_request(req_day):
        """Parse date from request or return today"""
        if req_day:
            year, month = (int(x) for x in req_day.split('-'))
            return date(year, month, day=1)
        return date.today()
    
    @staticmethod
    def get_day_activities(day, month, year):
        """Get activities for a specific day"""
        target_date = date(year, month, day)
        return Activite.objects.filter(
            date_debut__year=year,
            date_debut__month=month,
            date_debut__day=day
        ).order_by('date_debut')

# Helper class for calendar generation (same as before)
class Calendar:
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        self.cal = calendar.monthcalendar(year, month)

    def formatday(self, day, activites, weekday):
        activites_per_day = activites.filter(date_debut__day=day)
        d = ''
        for activite in activites_per_day:
            d += f'<li class="calendar-event" data-id="{activite.id}">{activite.date_debut.strftime("%H:%M")} - {activite.nom}</li>'
        
        if day != 0:
            has_events = 'has-events' if activites_per_day else ''
            today_class = 'today' if date.today() == date(self.year, self.month, day) else ''
            weekend_class = 'weekend' if weekday >= 5 else ''
            return f"<td class='{has_events} {today_class} {weekend_class}'><span class='date'>{day}</span><ul class='calendar-events'>{d}</ul></td>"
        return '<td class="noday"></td>'

    def formatweek(self, theweek, activites):
        week = ''
        for i, day in enumerate(theweek):
            weekday = i  # 0 = lundi, 6 = dimanche dans notre représentation
            week += self.formatday(day, activites, weekday)
        return f'<tr>{week}</tr>'

    def formatmonth(self, withyear=True):
        activites = Activite.objects.filter(
            date_debut__year=self.year, 
            date_debut__month=self.month
        )
        
        cal = f'<table class="calendar table table-bordered">\n'
        cal += f'<thead><tr class="month-header"><th colspan="7">{calendar.month_name[self.month]} {self.year}</th></tr>\n'
        cal += f'<tr class="weekdays">'
        for day in ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]:
            cal += f'<th class="header">{day}</th>'
        cal += f'</tr></thead>\n'
        
        # Ajout des jours du mois
        cal += '<tbody>\n'
        for week in self.cal:
            cal += f'{self.formatweek(week, activites)}\n'
        cal += '</tbody>\n'
        
        cal += '</table>'
        return cal