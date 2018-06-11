package ch.ethz.asltest;

import java.util.logging.Formatter;
import java.util.logging.LogRecord;

public class LogFormatter extends Formatter {

	@Override
	public String format(LogRecord record) {
		// TODO Is this it?
        return record.getMessage();
	}
}
